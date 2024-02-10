from flask import Flask, render_template, request, g
from flask_socketio import SocketIO, emit
import subprocess
import threading
import logging
import secrets

app = Flask(__name__)
socketio = SocketIO(app)

connected_users = 0
player_limit = 5
logging.basicConfig(level=logging.INFO)

def get_user_sessions():
    if 'user_sessions' not in g:
        g.user_sessions = {}
    return g.user_sessions

def start_application(client_id, port):
    # Replace this with the command to launch your application
    application_command = f"appium --port {port}"

    try:
        process = subprocess.Popen(application_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Store the process in the user_sessions dictionary
        user_sessions = get_user_sessions()
        user_sessions[client_id] = {'process': process, 'port': port}

        # Stream the output to the connected client
        while True:
            output = process.stdout.readline()
            if not output:
                break
            socketio.emit('application_output', {'client_id': client_id, 'output': output.strip()}, room=client_id)

        process.wait()

    except Exception as e:
        logging.error(f"Error running application: {e}")

    # Remove the process from user_sessions when the application is closed
    user_sessions = get_user_sessions()
    del user_sessions[client_id]

def update_player_status():
    socketio.emit('player_status', {'connected_users': connected_users, 'player_limit': player_limit})

@app.route('/')
def index():
    user_sessions = get_user_sessions()
    return render_template('index.html', player_limit=player_limit, user_sessions=user_sessions)

@socketio.on('connect')
def handle_connect():
    global connected_users, player_limit
    client_id = secrets.token_urlsafe(8)
    port = 5001 + connected_users  # Use a different port for each connected user
    
    if connected_users < player_limit:
        connected_users += 1
        update_player_status()
        socketio.emit('emulator_status', {'status': 'Connecting...'}, room=client_id)
        logging.info(f"Client connected with ID {client_id} on port {port}. Total connected users: {connected_users}")

        # Start the application and stream output to the connected client
        threading.Thread(target=start_application, args=(client_id, port)).start()

        return render_template('index.html', player_limit=player_limit, client_id=client_id, port=port)
    else:
        emit('player_limit_reached', {'message': 'Player limit reached. Please try again later.'}, room=client_id)
        logging.warning("Player limit reached. Connection rejected.")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    global connected_users
    if connected_users > 0:
        connected_users -= 1
        update_player_status()
        client_id = request.args.get('id')
        logging.info(f"Client disconnected with ID {client_id}. Total connected users: {connected_users}")

        # Terminate the associated application process
        user_sessions = get_user_sessions()
        if client_id in user_sessions:
            session = user_sessions[client_id]
            process = session['process']
            port = session['port']
            if process.poll() is None:
                process.terminate()
                logging.info(f"Application terminated for client ID {client_id} on port {port}")

if __name__ == '__main__':
    socketio.run(app, debug=False)
