# Communication Platform - Client
import time
import json
import socketio #Need this for exceptions

from server import PlayerInfo
from loggers import client_logger as logger
from common import JsonClient as Client
import socketio

# Method for sending a file to your opponent during a game.
class Player:
  def __init__(self):
    self.Name = None
    self.MessageQue = []
    self.PlayerInfo = None
    self.ReadyReturn = None
    self.SignalVictoryReturn = None
    self.RequestStartGameReturn = None
    self.SendInformationToOpponentReturn = None
    self.DisconnectReturn = None
    self.SetNameReturn = None
    self.sio = Client(logger=logger)
    self.CurrentOpponent = None
    self.__callbacks()
    self.inGame = False
    self.scoreBoard= None

  def __callbacks(self):

    def game_reset():
      pass #TODO when integrating Handle game reset
      #Call function here

    @self.sio.json_event(logging=True)
    def server_message(data):
      pass #TODO when integrating handle server_message 
      #Call function here

    @self.sio.json_event(logging=True)
    def game_info(data):
      self.CurrentOpponent = data['opponent']
      self.scoreBoard= data['score']
      #print(data['score'])
      #self.CurrentOpponent = {'id':data['opponentid'],'color':data['opponentcolor']}
      
      #pass #TODO when integrating handle game info
      #Call function here

    @self.sio.json_event(logging=True)
    def gameover(data):
      self.SignalVictoryReturn = int(data['code'])
      self.CurrentOpponent = None
      self.inGame = False
      #TODO can be extended for the Player not calling SignalVictory
      #Call function here

    @self.sio.json_event(logging=True)
    def msg_to_opponent(data):
      self.SendInformationToOpponentReturn = int(data['code'])

    @self.sio.json_event(logging=True)
    def msg_from_opponent(data):
      self.MessageQue.append(data)
   
    @self.sio.json_event(logging=True)
    def player_info(data):
      self.PlayerInfo = data

    @self.sio.json_event(logging=True)
    def custom_disconnect(data):
      self.DisconnectReturn = int(data['code'])

    @self.sio.json_event(logging=True)
    def start_game_request(data):
      code = int(data["code"])
      self.RequestStartGameReturn = code
      if code == 0:
        logger.debug("Request granted, started a new game!")
      elif code == -1:
        logger.debug("Requested denied, didn't start a new game.")

    @self.sio.json_event(logging=True)
    def ready(data):
      self.ReadyReturn = int(data['code'])

    @self.sio.json_event(logging=True)
    def set_name(data):
      code = int(data["code"])
      self.SetNameReturn = code
      if code == 0:
        self.Name = data['given_name']

    @self.sio.on('disconnect')
    def disconnect():
      logger.debug('Disconnected')

    @self.sio.on('*')
    def catch_all():
      logger.debug('Error')

    @self.sio.event
    def waiting():
      logger.debug("Waiting for your next game.")

  def ConnectToServer(self, ip='127.0.0.1', port=5000):
    try:
      self.sio.connect('http://' + ip+ ':' + str(port))
      logger.debug('Connected to ' + ip+ ':' +str(port))
      return 0
    except socketio.exceptions.ConnectionError as e:
      logger.debug('Failed to connect to server')
      return -1

  def Disconnect(self):
    logger.debug("Disconnect")
    try:
      self.sio.emit('custom_disconnect')
      self.WaitForDisconnect(1)
      self.sio.disconnect()
    except socketio.exceptions.BadNamespaceError as e:
      self.DisconnectReturn = -1

    ret = self.DisconnectReturn
    self.DisconnectReturn = None
    return ret

  def SendInformationToOpponent(self, information):
    logger.debug(f'SendInformationToOpponent("{information}")')
    self.sio.call('msg_to_opponent', information)
    ret = self.SendInformationToOpponentReturn
    self.SendInformationToOpponentReturn = None
    return ret

  def RequestStartGame(self):
    logger.debug("RequestStartGame")
    self.sio.call('start_game_request')
    ret = self.RequestStartGameReturn
    self.RequestStartGameReturn = None
    return ret

  def Ready(self):
    logger.debug("Ready")
    self.sio.call('ready')
    ret = self.ReadyReturn
    self.ReadyReturn = None
    return ret

  def SignalVictory(self, winner=None):
    logger.debug("Game over")
    self.sio.call('gameover', data={'winner': winner})
    ret = self.SignalVictoryReturn
    self.SignalVictoryReturn = None
    return ret

  def GetPlayerInfo(self):
    self.sio.call('player_data_request')
    logger.debug(self.PlayerInfo)
    return self.PlayerInfo

  # Set the player name
  def SetName(self, name):
    logger.debug("Set Name")
    self.sio.call('set_name', name)
    ret = self.SetNameReturn
    self.SetNameReturn = None
    return ret

  # Get Messages from Opponent
  # If Blocking, wait until there are messages available, specify timeout to break wait after timeout
  def GetMessageFromOpponent(self,blocking=False,timeout=None):
    if blocking:
      self.WaitForMessage(timeout=timeout)

    Messages = self.MessageQue
    self.MessageQue = []

    return Messages

  # Wait until there are messages in MessageQue
  def WaitForMessage(self,timeout):
    max = time.time() + timeout
    while len(self.MessageQue) < 1 and time.time() < max:
      time.sleep(1)

  # Wait until client gets disconnect signal from server DisconnectReturn
  def WaitForDisconnect(self, timeout):
    max = time.time() + timeout
    while self.DisconnectReturn is None and time.time() < max:
      time.sleep(1)

#if __name__ == "__main__":
