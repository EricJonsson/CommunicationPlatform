# Communication Platform - Client
import time
import json
import socketio #Need this for exceptions

from server import PlayerInfo
from loggers import client_logger as logger
from common import JsonClient as Client

# Method for sending a file to your opponent during a game.
class Player:
  PlayerInfo = None
  OpponentData = None

  def __init__(self):
    self.sio = Client(logger=logger)
    self.__callbacks()

  def __callbacks(self):

    @self.sio.json_event(logging=True)
    def msg_to_opponent(data):
      pass

    @self.sio.json_event(logging=True)
    def msg_from_opponent(data):
      pass

    @self.sio.json_event(logging=True)
    def game_info(data):
      pass

    @self.sio.json_event(logging=True)
    def player_info(data):
      self.PlayerInfo = data

    @self.sio.json_event(logging=True)
    def game_data(data):
      if not (data == "0" or data == "-1"):
        self.OpponentData = data
        # this is actually game data and not some success/fail code
        logger.debug(f"game_data: recieved a new game state {data}")

    @self.sio.json_event(logging=True)
    def start_game_request(data):
      code = data["code"]
      if code == 0:
        logger.debug("Request granted, started a new game!")
      elif code == -1:
        logger.debug("Requested denied, didn't start a new game.")

    @self.sio.json_event(logging=True)
    def ready(data):
      pass

    @self.sio.on('disconnect')
    def disconnect():
      logger.debug('Disconnected')

    @self.sio.on('*')
    def catch_all():
      logger.debug('Error')

    @self.sio.event
    def waiting():
      logger.debug("Waiting for your next game.")

  def ConnectToServer(self, ipAddress='127.0.0.1', port=5000):
    try:
      self.sio.connect('http://' + ipAddress + ':' + str(port))
      logger.debug('Connected to ' + ipAddress + ':' +str(port))
      return 0
    except socketio.exceptions.ConnectionError as e:
      logger.debug('Failed to connect to server')
      return -1

  def Disconnect(self):
    self.sio.disconnect()

  def SendInformationToOpponent(self, information):
    logger.debug(f'SendInformationToOpponent("{information}")')
    self.sio.emit('msg_to_opponent', information)
  
  def GetMessageFromOpponent(self, timeout=10):
    mustend = time.time() + timeout
    data = None
    while(self.OpponentData is None and time.time() < mustend):
      data = self.OpponentData
    print(data)
    return data

  def RequestStartGame(self):
    logger.debug("RequestStartGame")
    self.sio.emit('start_game_request')

  def Ready(self):
    logger.debug("Ready")
    self.sio.emit('ready')

  def SendGameData(self, GameState):
    logger.debug("SendGameData")
    self.sio.emit('game_data', GameState)

  def SignalVictory(self):
    logger.debug("Game over")
    self.sio.emit('gameover')

  def GetPlayerInfo(self):
    self.sio.call('player_data_request')
    logger.debug(self.PlayerInfo)
    return self.PlayerInfo

#if __name__ == "__main__":
