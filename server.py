# server.py

from flask import Flask, render_template
from flask_socketio import SocketIO
import subprocess
import threading

app = Flask(__name__)
socketio = SocketIO(app)

emulator_process = None

def start_emulator():
    global emulator_process
    emulator_command = "emulator -avd your_avd_name"
    emulator_process = subprocess.Popen(emulator_command, shell=True, stderr=subprocess.PIPE)

    while True:
        output = emulator_process.stderr.readline().decode('utf-8').strip()
        if not output:
            break
        socketio.emit('emulator_output', {'output': output})

    emulator_process.wait()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('emulator_status', {'status': 'Connecting...'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    if emulator_process and emulator_process.poll() is None:
        emulator_process.terminate()

if __name__ == '__main__':
    threading.Thread(target=start_emulator).start()
    socketio.run(app, debug=True)
