# Communication Platform - Server
from flask import Flask
import socketio

# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer():  # External
  Clients = []
  MaxConcurrentClients = 8
  sio = socketio.Server()
  app = None

  def __removeClientById(self, sid):
    for client in self.Clients:

      if client.compare(sid):
        self.Clients.remove(client)

  #All socketIO callbacks
  def __callbacks(self):
    @self.sio.event
    def connect(sid, environ, auth):
      if len(self.Clients) >= self.MaxConcurrentClients:
        self.sio.emit('server_full', to=sid)
        self.sio.disconnect(sid)
      else:
        new_client = Client(sid)
        self.Clients.append(new_client)
        print('Clients connected: ' + str(len(self.Clients))) # Ugly print

    @self.sio.event
    def disconnect(sid):
      self.__removeClientById(sid)
      print('Clients connected: ' + str(len(self.Clients)))

    @self.sio.event
    def message(sid, data):
      print('received message: ' + data + ' from ' + sid)

  def CreateServer(self, ip, port):
    self.app = Flask(__name__)
    self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
    self.__callbacks()
    self.app.run(ip, port)
  
  def __init__(self, maxConcurr = 8):
    self.MaxConcurrentClients = maxConcurr

#Unsure if we still need this
class ClientConnectionInfo:
  port = 1

class Client:
  ID = ''
  PlayerInfo = None

  def compare(self, sid):
    return sid == self.ID

  def __init__(self, ID):
    self.ID = ID


class PlayerInfo:
  GamesPlayed = 0
  GamesLeft = 0
  NumberOfWins = 0
  # Send the PlayerInfo to the player via the Socket

  def SendStatistics():
    pass


cs = CommunicationServer(8)
cs.CreateServer('127.0.0.1', 5000)
