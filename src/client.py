# Communication Platform - Client
import socketio
import time
import json

from server import PlayerInfo
from loggers import client_logger as logger

# Method for sending a file to your opponent during a game.
class Player:
  PlayerInfo = None

  def __init__(self):
    self.sio = socketio.Client()
    self.__callbacks()

  def __callbacks(self):

    @self.sio.event
    def msg_to_opponent(data):
      logger.debug('msg_to_opponent: ' + data)

    @self.sio.event
    def msg_from_opponent(data):
      logger.debug('msg_from_opponent: ' + data)

    @self.sio.event
    def game_info(data):
      logger.debug('game_info: ' + data)

    @self.sio.event
    def player_info(data):
      logger.debug('player_info: ' + data)
      self.PlayerInfo = json.loads(data)

    @self.sio.event
    def game_data(data):
      if data == "0" or data == "-1":
        logger.debug("game_data: " + data)
      else: # this is actually game data and not some success/fail code
        logger.debug("game_data: recieved a new game state " + data)


    @self.sio.event
    def start_game_request(data):
      logger.debug('start_game_request: ' + data)
      if int(data) == 0:
        logger.debug("Request granted, started a new game!")
      elif int(data) == -1:
        logger.debug("Requested denied, didn't start a new game.")

    @self.sio.event
    def ready(data):
      logger.debug('ready: ' + data)

    @self.sio.on('server_full')
    def full():
      logger.debug('Server is full :(')
      self.sio.disconnect()

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
    self.sio.connect('http://' + ipAddress + ':' + str(port))
    logger.debug('Connected to ' + ipAddress + ':' +str(port))

  def Disconnect(self):
    self.sio.disconnect()

  def SendInformationToOpponent(self, information):
    logger.debug('SendInformationToOpponent("' + information + '")')
    self.sio.emit('msg_to_opponent', information)

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

