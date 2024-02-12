from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
from flask_socketio import SocketIO
import subprocess
import cv2
import numpy as np
import pygetwindow as gw
import json
import atexit
import time

app = Flask(__name__)
socketio = SocketIO(app)

# List to store information about active containers
active_containers = []

# File to store container data
json_file = 'active_containers.json'

# Replace 'Nox Player' with the actual window title of the Nox Player instance
nox_window_title = 'Nox Player'

# Time threshold for considering a user disconnected (in seconds)
disconnect_threshold = 15

# Configuration variable for Nox executable location
nox_executable = '/Nox/bin/Nox.exe'  # Set the default location

def capture_nox_screen():
    nox_window = gw.getWindowsWithTitle(nox_window_title)[0]
    screenshot = np.array(nox_window.capture())
    _, buffer = cv2.imencode('.jpg', screenshot)
    return buffer.tobytes()

def save_active_containers():
    with open(json_file, 'w') as file:
        json.dump(active_containers, file, indent=2)

def load_active_containers():
    try:
        with open(json_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Load existing container data on server startup
active_containers = load_active_containers()

# Register save function to be called on server exit
atexit.register(save_active_containers)

def launch_nox_with_params(user_id):
    # Replace these parameters with the desired settings
    subprocess.Popen([
        nox_executable,  # Use the configured Nox executable location
        '-clone:' + user_id,
        '-title:Nox_' + user_id,
        '-lang:en',
        '-virtualKey:true',
        '-performance:high',
        '-root:false'
        # Add more parameters as needed
    ])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_id/<user_id>')
def create_id_without_start(user_id):
    # Add information about the new container to active_containers without starting the app
    active_containers.append({"user_id": user_id, "active": False, "last_activity": time.time()})
    return f'ID {user_id} created successfully without starting the app!'

@app.route('/start_app/<user_id>', methods=['POST'])
def start_app(user_id):
    # Start the app for the specified user_id
    for container in active_containers:
        if container["user_id"] == user_id:
            if not container["active"]:
                launch_nox_with_params(user_id)
                container["active"] = True
            break

    return redirect(url_for('stream', user_id=user_id))

@app.route('/stream/<user_id>')
def stream(user_id):
    # Check if the requested user_id has an active container
    if any(container["user_id"] == user_id and container["active"] for container in active_containers):
        def generate():
            while True:
                # Update the last activity time for the user
                for container in active_containers:
                    if container["user_id"] == user_id:
                        container['last_activity'] = time.time()
                        break
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + capture_nox_screen() + b'\r\n\r\n')

        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return 'No active container for this ID.'

@app.route('/close_app/<user_id>', methods=['POST'])
def close_app(user_id):
    # Use -quit to close the Nox App Player instance
    subprocess.run([nox_executable, '-clone:' + user_id, '-quit'])

    # Set the container as inactive
    for container in active_containers:
        if container["user_id"] == user_id:
            container["active"] = False
            break

    return jsonify({'success': True})

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.args.get('user_id')

    # Check if the user_id is in active_containers
    for container in active_containers:
        if container["user_id"] == user_id:
            # Check if the user has been inactive for more than the threshold
            if time.time() - container.get('last_activity', 0) > disconnect_threshold:
                # Use -quit to close the Nox App Player instance
                subprocess.run([nox_executable, '-clone:' + user_id, '-quit'])

                # Set the container as inactive
                container["active"] = False
            break

if __name__ == '__main__':
    socketio.run(app, debug=True)
