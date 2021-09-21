# Communication Platform - Server
from flask import Flask
import socketio

# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer():  # External
  def __init__(self, maxConcurr=8):
    self.MaxConcurrentClients = maxConcurr
    self.Clients = []
    self.sio = socketio.Server()
    self.app = None

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

    @self.sio.event
    def msg_opponent(sid, data):
      print('msg_opponent: ' + data + ' from ' + sid)
      print('Clients: ' + str(len(self.Clients)))
      print(self.Clients[0].get_id())

  def CreateServer(self, ip, port):
    self.app = Flask(__name__)
    self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
    self.__callbacks()
    self.app.run(ip, port)
  


class Client:
  def __init__(self, ID):
    self.ID = ID
    self.PlayerInfo = PlayerInfo()

  def compare(self, sid):
    return sid == self.ID

  def get_id(self):
    return self.ID


class PlayerInfo:
  def __init__(self):
    GamesPlayed = 0
    GamesLeft = 0
    NumberOfWins = 0

  # Send the PlayerInfo to the player via the Socket
  def SendStatistics():
    pass


if __name__ == "__main__":
  cs = CommunicationServer(8)
  cs.CreateServer('127.0.0.1', 5000)
