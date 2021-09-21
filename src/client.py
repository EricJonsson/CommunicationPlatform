# Communication Platform - Client
import socketio
import time

# Method for sending a file to your opponent during a game.
class Player:
  def __init__(self):
    self.sio = socketio.Client()
    self.__callbacks()

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

  def ConnectToServer(self, ipAddress='127.0.0.1', port=5000):
    self.sio.connect('http://' + ipAddress + ':' + str(port))
    print('Connected to ' + ipAddress + ':' +str(port))

  def Disconnect(self):
    self.sio.disconnect()

  def SendInformationToOpponent(self, information):
    self.sio.emit('msg_opponent', information)
    return 0

if __name__ == "__main__":
  player = Player()
  player.ConnectToServer('127.0.0.1', 5000)
  time.sleep(2)
  player.SendInformationToOpponent("Hello dear opponent!")
  time.sleep(2)
  player.Disconnect()
