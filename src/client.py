# Communication Platform - Client
import socketio
import time

# Method for sending a file to your opponent during a game.
class Player:
  sio = socketio.Client()

  def __callbacks(self):

    @self.sio.on('server_full')
    def full():
      print('Server is full :(')
      self.sio.disconnect()
    
    @self.sio.on('disconnect')
    def disconnect():
      print('Disconnected')

    @self.sio.on('*')
    def catch_all():
      print('Error')

  def __init__(self):
    self.__callbacks()

  def SendInformationToOpponent(self, information):
    return 0

  def ConnectToServer(self, ipAddress='127.0.0.1', port=5000):
    self.sio.connect('http://' + ipAddress + ':' + str(port))
    print('Connected to ' + ipAddress + ':' +str(port))

  def Disconnect(self):
    self.sio.disconnect()


player = Player()
player.ConnectToServer('127.0.0.1', 5000)
time.sleep(2)
player.Disconnect()