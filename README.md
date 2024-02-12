# Nox Player Controller

This project is a Flask-based web application that serves as a controller for Nox Player instances. It allows users to create unique IDs, start and stop Nox Player instances associated with those IDs, and view live streams from the instances.

## Features

- **Create ID Without Starting App**: Users can create a unique ID without immediately starting the Nox Player app.

- **Start App and Stream**: Users can start the Nox Player app associated with a specific ID and view the live stream from that instance.

- **Live Stream Viewer**: The web application provides a live stream viewer to monitor the Nox Player instances.

- **ID Management**: The application maintains a list of active containers with information about their status, last activity time, and user ID.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/nox-player-controller.git
   cd nox-player-controller
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set the correct Nox Player executable location in the `app.py` file:

   ```python
   # Configuration variable for Nox executable location
   nox_executable = '/Nox/bin/Nox.exe'  # Set the default location
   ```

4. Run the application:

   ```bash
   python app.py
   ```

## Usage

1. Open the application in your web browser: [http://localhost:5000/](http://localhost:5000/)

2. **Create New ID**: Enter a unique user ID in the provided text box and click the "Create ID" button.

3. **Start App and Stream**: Enter the created User ID in the text box and click the "Start App and Stream" button to initiate the Nox Player app and view the live stream.

4. **Live Stream Viewer**: The live stream viewer section displays the active containers and their status.

   - **Active**: The Nox Player instance is currently running.
   - **Inactive**: The Nox Player instance is not running.

5. **Close App**: To stop an active Nox Player instance, enter the User ID and click the "Close App" button.

6. **Disconnect Handling**: The application automatically handles disconnections. If a user has been inactive for more than the threshold (15 seconds), the associated Nox Player instance will be closed, and the container will be marked as inactive.
