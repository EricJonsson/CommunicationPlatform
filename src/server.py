# Communication Platform - Server
from flask import Flask, render_template
from flask_socketio import SocketIO



# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer:  # External
  Clients = []
  MaxConcurrentClients = 8
  _socketio = None

  def __init__(self, debug=False):
    app = Flask(__name__)
#    self._debug = debug
    @_socketio.on('message')
    def handle_message(data):
      print('received message: ' + data)


  #Maybe we cou
  def CreateServer(self):
    app.config['SECRET_KEY'] = 'secret!'
    self._socketio = SocketIO(app)
    self._socketio.run(app, '127.0.0.1', 17432)



  
class ClientConnectionInfo:
  port = 1


class Client:
  Socket = None
  PlayerInfo = None


class PlayerInfo:
  GamesPlayed = 0
  GamesLeft = 0
  NumberOfWins = 0
  # Send the PlayerInfo to the player via the Socket

  def SendStatistics():
    pass


cs = CommunicationServer()
cs.CreateServer()
