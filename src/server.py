# Communication Platform - Server
from typing import Optional, TypeVar
from flask import Flask
import socketio
import time
import itertools
import random
import json
import textwrap
from loggers import server_logger as logger
from common import JsonServer as Server
import threading

#from socketio.server import Server


# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer():  # External
  def __init__(self, maxConcurr=8):
    self.MaxConcurrentClients = maxConcurr
    self.Clients = []
    self.sio = Server()
    self.app = None
    self.ActiveGames = []
    self.TournamentGames = []
    self.ConcludedGames = []

  # Generates the next round. i.e. moves as many games as
  # possible from TournamentGames to ActiveGames without overlap
  def generateRound(self):

    if len(self.ActiveGames) > 0:
      logger.debug('Error couldn\'t generate round - Round still in progress')
      return -1

    for t_game in self.TournamentGames:
      contains = False
      for a_game in self.ActiveGames:
        contains = a_game.checkOverlap(t_game) or contains
      if not contains: # start the game
        self.ActiveGames.append(t_game)
        self.sio.emit('game_info', {
            'data': 'you are now in a game vs {}'.format(t_game.PlayerB)
        }, to=t_game.PlayerA.get_id()) # msg PlayerA that they are playing vs PlayerB
        self.sio.emit('game_info', {
            'data': 'you are now in a game vs {}'.format(t_game.PlayerA)
        }, to=t_game.PlayerB.get_id()) # vice-versa


    #Remove Active games from tournament-list
    for game in self.ActiveGames:
      self.TournamentGames.remove(game)

    return 0

  #Fills TournamentGames with all matches for the tournament
  def generateTournament(self):
    if len(self.TournamentGames) != 0:
      logger.debug('ERROR: couldn\'t generate tournament')
      return -1
    combinations = list(itertools.combinations(self.Clients, 2))

    for combination in combinations:
      game = Game(PlayerA = combination[0], PlayerB= combination[1])
      self.TournamentGames.append(game)

    random.shuffle(self.TournamentGames)
    return 0

  def __removeClientById(self, sid):
    for client in self.Clients:
      if client == sid:
        self.Clients.remove(client)

  #All socketIO callbacks
  def __callbacks(self):

    @self.sio.event
    def connect(sid, environ, auth):
      if len(self.Clients) >= self.MaxConcurrentClients:
        raise socketio.exceptions.ConnectionRefusedError('Server is full')
      else:
        new_client = Client(sid)
        self.Clients.append(new_client)
        logger.debug('Clients connected: {}'.format(len(self.Clients))) # Ugly print

    @self.sio.event
    def disconnect(sid):
      self.__removeClientById(sid)
      game = self.FindActiveGameBySid(sid)
      if game:
        opponent = (game.PlayerA if game.PlayerA != sid else game.PlayerB).get_id()
        game.ConcludeGame(winner=opponent)
      logger.debug('Clients connected: {}'.format(len(self.Clients)))

    # @self.sio.event # not used currently
    # def message(sid, data):
    #   logger.debug('received message: ' + data + ' from ' + sid)

    @self.sio.json_event
    def msg_to_opponent(sid, data):
      logger.debug(f'msg_to_opponent: {data} from {sid}')
      #logger.debug('Clients: {}'.format(len(self.Clients)))
      #logger.debug(self.Clients[0])

      if game := self.FindActiveGameBySid(sid):
        if sid == game.PlayerA:
          opponent = game.PlayerB.get_id()
        else:
          opponent = game.PlayerA.get_id()

        if opponent is not None: # if opponent is not None an opponent exists, meaning the player is in an active game
          self.sio.emit('msg_to_opponent', {
              'opponent': '0'
          }, to=sid) # response to the one calling
          self.sio.emit('msg_from_opponent', {
              'data': f'Opponent {sid} sent "{data}".'
          }, to=opponent)
          logger.debug(f'message sent to from {sid} to opponent {opponent}')
        else:
          #self.sio.emit('msg_to_opponent', 'You are not in a game, no opponent exists.', to=sid)
          self.sio.emit('msg_to_opponent', {
              'opponent': '-1'
          }, to=sid)
          logger.debug(f'Player: {sid} is not in game, msg_to_opponent.')

    @self.sio.event
    def start_game_request(sid):
      logger.debug(f'start_game_request: from {sid}')
      code = self.StartGame()
      self.sio.emit('start_game_request', {"code": str(code)}, to=sid)

    @self.sio.on('player_data_request')
    def player_data_request(sid):
      playerData = None
      for client in self.Clients:
        if client == sid:
          playerData = client.PlayerInfo

      if playerData is not None:
        logger.debug('sending')
        self.sio.emit('player_info', data=playerData.__dict__, to=sid)

    @self.sio.event
    def ready(sid):
      logger.debug('ready: from ' + sid)

      # Sets client.Ready to true
      for client in self.Clients:
        if client == sid:
          client.Ready = True
          self.sio.emit('ready', {"code": 0}, to=sid)
          break
      # NOTE: Currently does not have the case if sending -1 (fail) for a ready() call


      # Check if all players are ready, if they are we start a game!
      ready_counter = 0
      for client in self.Clients:
        if client.Ready:
          ready_counter += 1

      if ready_counter == len(self.Clients): # everyone is ready
        code = self.StartGame()
      else:
        logger.debug(f'Players Ready: {ready_counter}/{len(self.Clients)}, waiting for all.')

    @self.sio.json_event
    def game_data(sid, data):
      logger.debug(f'game_data: {data} from {sid}')
      opponent = self.GetOpponent(sid)
      if opponent is not None: # An opponent exists, the player is currently playing
        self.sio.emit('game_data', data, to=opponent) # relay to opponent!
        self.sio.emit('game_data', {"data": 0}, to=sid) # succesfully sent response
      else:
        self.sio.emit('game_data', {"data": -1}, to=sid) # error code response

    @self.sio.event
    def gameover(sid):
      if game := self.FindActiveGameBySid(sid):
        game.ConcludeGame(sid)
        self.ConcludedGames.append(game)

        # remove the game from active games
        for a_game in self.ActiveGames:
          if a_game.PlayerA == game.PlayerA and a_game.PlayerB == game.PlayerB:
            self.ActiveGames.remove(game)


        self.sio.emit('waiting', to=game.PlayerA.get_id())
        self.sio.emit('waiting', to=game.PlayerB.get_id())

        if len(self.TournamentGames) > 0: #there's an ongoing tournament, since a game is over we can try to start new games!
          code = self.generateRound()
          #logger.debug("###### GENERATE ROUND: " + str(code))
          #logger.debug("Active Games: " + str(len(self.ActiveGames)))
          #logger.debug("Tournament Games: " + str(len(self.TournamentGames)))

          if code == 0:
            logger.debug('Started Game: ' + str(game.PlayerA) + ' vs ' + str(game.PlayerB) + '.')
          else:
            logger.debug("Couldn't start any new games at this point.")
      else:
        logger.debug(f'ERROR: Event sent by inactive player `{sid}`.')

  def FindActiveGameBySid(self, sid: str) -> Optional[TypeVar("Game")]:
    for game in self.ActiveGames:
      if (sid == game.PlayerA.get_id() or sid == game.PlayerB.get_id()) and game.Active: # the player 'sid' is playing in the game and the game is still going on
        return game

  def CreateServer(self, ip, port):
    # Create new thread with target _InternalCreateServer
    thread = threading.Thread(target=self._InternalCreateServer, args=[ip,port])
    # Set Process to daemon to destroy when main thread finishes
    thread.daemon = True
    thread.start()
    return thread

  # Original Create Server Implementation
  def _InternalCreateServer(self,ip,port):
    self.app = Flask(__name__)
    self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
    self.__callbacks()
    self.app.run(ip, port)

  def StartGame(self):
    if len(self.ActiveGames) != 0:
      logger.debug("Cannot start a new game, a game is already going on.")
      return -1

    logger.debug("------STARTING A GAME------")
    # Starts a game, different cases based on number of players
    if len(self.Clients) == 1:
      # only 1 player, start AI match
      logger.debug("Starting AI Game (not implemented)")
      return -1
    if len(self.Clients) == 2:
      # 2 players, match them up for a game
      game = Game(self.Clients[0], self.Clients[1])
      self.ActiveGames.append(game)
      logger.debug(game)
      logger.debug('Started Game: ' + str(game.PlayerA) + ' vs ' + str(game.PlayerB) + '.')
      self.sio.emit('game_info', {
          'data': 'you are now in a game vs {game.PlayerB}'
      }, to=game.PlayerA.get_id()) # msg PlayerA that they are playing vs PlayerB
      self.sio.emit('game_info', {
          'data': 'you are now in a game vs {game.PlayerA}'
      }, to=game.PlayerB.get_id()) # vice-versa


    if len(self.Clients) > 2:
      # tournament
      logger.debug("------TOURNAMENT MODE------")
      if len(self.ActiveGames) != 0: # already exists ongoing games for some reason, error
        return -1

      self.generateTournament() # generate all games to be played into self.TournamentGames
      logger.debug("generated tournament :)")
      if len(self.TournamentGames) <= 0:
        return -1

      code = self.generateRound()
      if code == -1: #
        logger.debug("Error: Couldn't generate a new round")
        return -1

    return 0

  def GetOpponent(self, sid):
    # Searches through all games and finds an opponent for the given player (sid) if one exists.
    opponent = None
    for game in self.ActiveGames:
      if (sid == game.PlayerA or sid == game.PlayerB) and game.Active: # the player 'sid' is playing in the game and the game is still going on
        if sid == game.PlayerA:
          opponent = game.PlayerB.get_id()
        else:
          opponent = game.PlayerA.get_id()
        break
    return opponent



class Client:
  def __init__(self, ID):
    self.ID = ID
    self.Ready = False
    self.PlayerInfo = PlayerInfo()

  def __str__(self):
    return f'[SID: {self.ID}]' # might want to add playerinfo here later on

  def __eq__(self, other):
    if isinstance(other, Client):
      return self.ID == other.ID
    elif isinstance(other, str):
      return self.ID == other
    else:
      return self == other

  def get_id(self):
    return self.ID

  def lose(self):
    self.PlayerInfo.lose()

  def win(self):
    self.PlayerInfo.win()

  def addGameLeft(self):
    self.PlayerInfo.addGameLeft()


class PlayerInfo:
  def __init__(self):
    self.GamesPlayed = 0
    self.GamesLeft = 0
    self.NumberOfWins = 0

  def lose(self):
    self.GamesPlayed += 1
    self.GamesLeft -= 1

  def win(self):
    self.GamesPlayed += 1
    self.GamesLeft -= 1
    self.NumberOfWins += 1

  def addGameLeft(self):
    self.GamesLeft += 1

class Game:
  def __init__(self, PlayerA=None, PlayerB=None, Active=True, Winner=None):
    self.PlayerA = PlayerA
    self.PlayerB = PlayerB
    self.Active = Active
    self.Winner = Winner

    self.PlayerA.addGameLeft()
    self.PlayerB.addGameLeft()

  def __str__(self):
    return textwrap.dedent(f'''\
        PlayerA: {self.PlayerA}
        PlayerB: {self.PlayerB}
        Active: {self.Active}
        Winner: {self.Winner}
        ----------------------------\
    ''')

  #Checks if any of the players occur in both games
  def checkOverlap(self, other):
    overlap = (self.PlayerA == other.PlayerA) or (self.PlayerA == other.PlayerB) or (self.PlayerB == other.PlayerA) or(self.PlayerB == other.PlayerB)
    return overlap


  def ConcludeGame(self, winner: str):
    self.Active = False
    self.Winner = winner
    if self.PlayerA == winner:
      self.PlayerA.win()
      self.PlayerB.lose()
    else:
      self.PlayerA.lose()
      self.PlayerB.win()
    return 0

  #TEST by hand for the tournament and round generation
  #cs.Clients = [Client(0), Client(1), Client(2), Client(3)]
  #cs.generateTournament()
  #while(len(cs.TournamentGames) > 0):
    #cs.ActiveGames = []
    #cs.generateRound()
    #logger.debug('===========================================================================')
    #for game in cs.ActiveGames:
      #logger.debug(game)
