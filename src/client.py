# Communication Platform - Client
import socketio
import time

# Method for sending a file to your opponent during a game.
class Player:
  def __init__(self):
    self.sio = socketio.Client()
    self.__callbacks()

  def __callbacks(self):

    @self.sio.event
    def msg_to_opponent(data):
      print('msg_to_opponent: ' + data)

    @self.sio.event
    def msg_from_opponent(data):
      print('msg_from_opponent: ' + data)

    @self.sio.event
    def game_info(data):
      print('game_info: ' + data)

    @self.sio.event
    def game_data(data):
      if data == "0" or data == "-1":
        print("game_data: " + data)
      else: # this is actually game data and not some success/fail code
        print("game_data: recieved a new game state " + data)


    @self.sio.event
    def start_game_request(data):
      print('start_game_request: ' + data)
      if int(data) == 0:
        print("Request granted, started a new game!")
      elif int(data) == -1:
        print("Requested denied, didn't start a new game.")

    @self.sio.event
    def ready(data):
      print('ready: ' + data)

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
    print('SendInformationToOpponent("' + information + '")')
    self.sio.emit('msg_to_opponent', information)

  def RequestStartGame(self):
    print("RequestStartGame")
    self.sio.emit('start_game_request')

  def Ready(self):
    print("Ready")
    self.sio.emit('ready')

  def SendGameData(self, GameState):
    print("SendGameData")
    self.sio.emit('game_data', GameState)

if __name__ == "__main__":

  val = int(input("Choose player 1 or 2: "))

  if val == 1:
    player = Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    GameState = "[1,0,1] or sth"
    player.SendGameData(GameState)
    time.sleep(2)
    player.Ready()
    time.sleep(4)
    player.SendGameData(GameState)
    time.sleep(1000)
    player.Disconnect()
  elif val == 2:
    player = Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    player.SendInformationToOpponent("Hello dear opponent!")
    time.sleep(2)
    player.Ready()
    time.sleep(6)
    player.SendInformationToOpponent("Hello dear opponent!")
    time.sleep(1000)
    player.Disconnect()
  else: # do whatever you want here :)
    pass
