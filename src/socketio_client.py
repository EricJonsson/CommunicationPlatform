import socketio

sio = socketio.Client()
sio.connect('http://127.0.0.1:17432')
sio.send('yoyoyoy')