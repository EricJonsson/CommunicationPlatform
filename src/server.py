# Communication Platform - Server
from flask import Flask
import socketio

# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer():  # External
  Clients = []
  MaxConcurrentClients = 8
  SIO = socketio.Server()
  app = None

  def callbacks(self):

    @self.SIO.event
    def connect(sid, environ, auth):
      self.Clients.append(sid)
      print(self.Clients)
    @self.SIO.event
    def disconnect(sid):
      self.Clients.remove(sid)
      print(self.Clients)

    @self.SIO.event
    def message(sid, data):
      print('received message: ' + data + ' from ' + sid)

  def CreateServer(self):
    self.app = Flask(__name__)
    self.app.wsgi_app = socketio.WSGIApp(self.SIO, self.app.wsgi_app)
    self.callbacks()
    self.app.run('127.0.0.1', 5000)

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
