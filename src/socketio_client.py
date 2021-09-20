import socketio

sio = socketio.Client()
sio.connect('http://127.0.0.1:5000')
sio.send('yoyoyoy')
sio.disconnect()