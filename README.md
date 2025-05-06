# Django EC2 WebSocket Terminal

This project is a Django-based web application that provides a browser-based terminal interface using WebSockets and [xterm.js](https://xtermjs.org/). It is designed to stream terminal sessions (e.g., from an EC2 instance) to the frontend in real time.

## Features
- **Django + Channels**: Uses Django Channels for WebSocket support.
- **EC2 Integration**: Ready for backend logic to stream terminal output from an AWS EC2 instance (via SSH, to be implemented in `TerminalConsumer`).
- **xterm.js Frontend**: Presents a fully interactive terminal in the browser using xterm.js.
- **Simple Django Template**: Uses a minimal HTML template for easy customization.

## Project Structure
```
django-vm-websocket/
├── manage.py
├── requirements.txt
├── vmwebsocket/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── terminal/
│   ├── consumers.py
│   ├── routing.py
│   ├── views.py
│   └── templates/terminal/terminal.html
└── ...
```

## Setup Instructions

### 1. Clone and Prepare Environment
```bash
# Clone the repository
# cd into the project directory
python3 -m venv ../env-vm-performance
source ../env-vm-performance/bin/activate
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Start the Development Server
```bash
python manage.py runserver
```

### 5. Access the Terminal
Open your browser and go to [http://localhost:8000/](http://localhost:8000/)

You should see a terminal interface powered by xterm.js. Typing in the terminal will echo your input (for now).

## WebSocket & EC2 Streaming
- The WebSocket endpoint is at `/ws/terminal/`.
- The backend logic for streaming an actual EC2 shell session should be implemented in `terminal/consumers.py` (see the `TerminalConsumer` class).
- You can use `boto3` and `asyncssh` (or similar) to connect to EC2 and stream the shell output.

## Customization
- **Frontend**: Edit `terminal/templates/terminal/terminal.html` to customize the look or add features.
- **Backend**: Extend `TerminalConsumer` to handle authentication, EC2 connection, and streaming.

## Requirements
- Python 3.8+
- Django 5.2+
- channels 4.0+
- boto3 1.38+
- uvicorn

## License
MIT or your preferred license.

## Running with ASGI Servers

This project requires an ASGI server to support WebSockets. You can use either Daphne or Uvicorn:

### Using Uvicorn (recommended for local development)
```bash
uvicorn vmwebsocket.asgi:application --host 0.0.0.0 --port 8000
```

**Note:** Do not use `python manage.py runserver` for WebSocket support.
