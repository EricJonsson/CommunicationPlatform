# Communication Platform - Server
from typing import Optional, TypeVar
from flask import Flask
import socketio
import itertools
import random
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
    self.AICounter = 0
    self.TournamentMode = False

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
        if not t_game.PlayerA.isAI:
          self.sio.emit('game_info', {
            'opponent':
            {'id': str(t_game.PlayerB.Name),
              'color': 'white'
            },
            'AI': t_game.PlayerB.isAI,
            'difficulty': t_game.PlayerB.difficulty
          }, to=t_game.PlayerA.get_id())  # msg PlayerA that they are playing vs PlayerB

        if not t_game.PlayerB.isAI:
          self.sio.emit('game_info', {
            'opponent': 
            {'id': str(t_game.PlayerA.Name),
              'color': 'black'
            },
            'AI': t_game.PlayerA.isAI,
            'difficulty': t_game.PlayerA.difficulty
          }, to=t_game.PlayerB.get_id()) # vice-versa

    for game in self.ActiveGames: #Remove all active games from TrounamentGames
      if game.PlayerA.isAI and game.PlayerB.isAI:
        self._concludeAIGame(game)
        self.ConcludedGames.append(game)

      self.TournamentGames.remove(game)

    return 0
  
  def _concludeAIGame(self, game): #Randomizes a winner in the case that both players are AIs
    winner = random.randint(0, 1)
    if winner == 1:
      game.ConcludeGame(winner = game.PlayerA.get_id())
    else:
      game.ConcludeGame(winner = game.PlayerB.get_id())

  def _concludePlayerGames(self, player):
    idx = 0
    while idx < len(self.TournamentGames):
      t_game = self.TournamentGames[idx]
      if t_game.PlayerA == player or t_game.PlayerB == player:
        t_game.ConcludeGame(t_game.PlayerB if t_game.PlayerA == player else t_game.PlayerA)
        self.ConcludedGames.append(t_game)
        self.TournamentGames.remove(t_game)
      else:
        idx += 1

  #Fills TournamentGames with all matches for the tournament
  def generateTournament(self):
    if len(self.TournamentGames) != 0:
      logger.debug('ERROR: couldn\'t generate tournament')
      return -1
    combinations = list(itertools.combinations(self.Clients, 2))

    for combination in combinations:
      game = Game(PlayerA = combination[0], PlayerB= combination[1])
      self.TournamentGames.append(game)
    self.TournamentStarted = True

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
      elif self.TournamentStarted:
        raise socketio.exceptions.ConnectionRefusedError('Tournament already started.')
      else:
        new_client = Client(sid)
        new_client.Name = sid
        self.Clients.append(new_client)
        logger.debug('Clients connected: {}'.format(len(self.Clients))) # Ugly print

    @self.sio.event
    def disconnect(sid):
      self.__removeClientById(sid)
      game = self.FindActiveGameBySid(sid)
      self._concludePlayerGames(sid)
      if game:
        opponent = (game.PlayerA if game.PlayerA != sid else game.PlayerB).get_id()
        self._concludeGame(game, winner=opponent)
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
          #self.sio.emit('msg_to_opponent', {
          #    'code': 0
          #}, to=sid) # response to the one calling
          self.sio.emit('msg_to_opponent', {'code': 0}, to=sid)
          self.sio.emit('msg_from_opponent', {
            'opponent':sid,
            'data': data
          }, to=opponent)
          logger.debug(f'message sent to from {sid} to opponent {opponent}')
      else:
        self.sio.emit('msg_to_opponent', {'code': -1}, to=sid)
        #self.sio.emit('msg_to_opponent', 'You are not in a game, no opponent exists.', to=sid)
        #self.sio.emit('msg_to_opponent', {
        #    'code': -1
        #}, to=sid)
        logger.debug(f'Player: {sid} is not in game, msg_to_opponent.')

    @self.sio.event
    def start_game_request(sid):
      logger.debug(f'start_game_request: from {sid}')
      code = self.StartGame()
      self.sio.emit('start_game_request', {'code': str(code)}, to=sid)

    @self.sio.event
    def set_name(sid, data):
      logger.debug(f'set_name: from {sid} data {data}')
      code, given_name = self.SetPlayerName(sid, data.strip('"'))
      self.sio.emit('set_name', {'code': str(code), 'given_name': given_name}, to=sid)

    @self.sio.event
    def custom_disconnect(sid):
      logger.debug(f'custom_disconnect: from {sid}')
      self.sio.emit('custom_disconnect', {'code': 0}, to=sid)

    @self.sio.on('player_data_request')
    def player_data_request(sid):
      playerData = None
      for client in self.Clients:
        if client == sid:
          playerData = client.PlayerInfo

      if playerData is not None:
        logger.debug(playerData.__dict__)
        self.sio.emit('player_info', data=playerData.__dict__, to=sid)

    @self.sio.event
    def ready(sid):
      logger.debug('ready: from ' + sid)

      # Sets client.Ready to true
      for client in self.Clients:
        if client == sid:
          client.Ready = True
          self.sio.emit('ready', {'code': 0}, to=sid)
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

    @self.sio.event
    def gameover(sid):
      if game := self.FindActiveGameBySid(sid):
        self._concludeGame(game, winner=sid)

        if len(self.ActiveGames) == 0 and len(self.TournamentGames) == 0 and self.TournamentMode: # all games for the tournament are complete!
          logger.debug('The tournament is over.')
          self.TournamentMode = False

          # announce to everyone in the tournament that the tournament is over
          for client in self.Clients:
            self.sio.emit('game_info', {"code": 1, "data": "The tournament is over.",'opponent':None}, to=client.get_id())
      else:
        self.sio.emit('gameover', {"code": -1}, to=sid)
        logger.debug(f'ERROR: Event sent by inactive player `{sid}`.')

  def FindActiveGameBySid(self, sid: str) -> Optional[TypeVar("Game")]:
    assert isinstance(sid, str)
    for game in self.ActiveGames:
      if (game.PlayerA == sid or game.PlayerB == sid) and game.Active: # the player 'sid' is playing in the game and the game is still going on
        return game

  def GetNumPlayers(self):
    return len(self.Clients)

  def AddAI(self, difficulty = 1):
    if self.GetNumPlayers() >= self.MaxConcurrentClients:
      return -1

    AI = Client(ID=str(self.AICounter), AI=True, difficulty=difficulty)
    AI.Ready = True
    self.AICounter += 1
    self.Clients.append(AI)
    return 0

  def _concludeGame(self, game, winner):
    game.ConcludeGame(winner=winner)
    self.ConcludedGames.append(game)

    #Remove active game
    self.ActiveGames.remove(game)

    self.sio.emit('gameover', {"code": 1, "winner": winner}, to=game.PlayerA.get_id())
    self.sio.emit('gameover', {"code": 1, "winner": winner}, to=game.PlayerB.get_id())

    if len(self.ActiveGames) == 0 and len(self.TournamentGames) > 0: #there's an ongoing tournament, since a game is over we can try to start new games! 
      code = self.generateRound()
      if code == 0:
        logger.debug("Started a new Round, all games completed")

  def CreateServer(self, ip = '127.0.0.1', port=5000):
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
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
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
      logger.debug("Waiting for Player or AI")
    if len(self.Clients) == 2:
      # 2 players, match them up for a game
      game = Game(self.Clients[0], self.Clients[1])
      self.ActiveGames.append(game)
      logger.debug(game)
      logger.debug('Started Game: ' + str(game.PlayerA) + ' vs ' + str(game.PlayerB) + '.')
      self.sio.emit('game_info', {'opponent':{'id': game.PlayerA.Name, 'color':'white'}
      }, to=game.PlayerA.get_id()) # msg PlayerA that they are playing vs PlayerB
      self.sio.emit('game_info', {'opponent':{'id': game.PlayerB.Name, 'color':'black'}
      }, to=game.PlayerB.get_id()) # vice-versa
      '''
      self.sio.emit('game_info', {
          'data': f'you are now in a game vs {game.PlayerB}'
      }, to=game.PlayerA.get_id()) # msg PlayerA that they are playing vs PlayerB
      self.sio.emit('game_info', {
          'data': f'you are now in a game vs {game.PlayerA}'
      }, to=game.PlayerB.get_id()) # vice-versa
'''

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
      self.TournamentMode = True

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

  def ResetTournament(self):
    self.ActiveGames = []
    self.ConcludedGames = []
    self.TournamentGames = []

    players = [client for client in self.Clients if not client.isAI]
    self.Clients = players
    for client in self.Clients:
      client.reset()
      self.sio.emit('game_reset', to = client.get_id())
    return 0

  def SetPlayerName(self, sid, name):
    name_exists = False
    for client in self.Clients:
      if client.Name == name:
        name_exists = True
        break

    if name_exists: # auto generate some additional numbers to make the user's name unique
        while name_exists:
          suffix = random.randint(1000,9999)
          new_name = name + "#" + str(suffix)
          new_name_exists = False
          for client in self.Clients:
            if client.Name == new_name:
              new_name_exists = True
              break
          name_exists = new_name_exists
        name = new_name

    # set the name for the client
    for client in self.Clients:
      if client.get_id() == sid:
        client.Name = name
    return 0, name

  def GetTournamentData(self):
    if not self.TournamentMode:
      return -1

    data = []
    for client in self.Clients:
      client_data = {
        'Name': client.Name,
        'Wins': client.PlayerInfo.NumberOfWins,
        'ID': client.ID,
        'AI': client.isAI
      }
      data.append(client_data)

    return data

  def SendToPlayer(self, name, info):
    playerID = ''
    for client in self.Clients:
      if client.Name == name:
        playerID = client.ID

    if playerID == '':
      return -1
    
    self.sio.emit('server_message', info, to=playerID)
    return 0

class Client:
  def __init__(self, ID, AI = False, difficulty = 1):
    self.ID = ID
    self.Name = None
    self.Ready = False
    self.PlayerInfo = PlayerInfo()
    self.isAI = AI 
    self.difficulty = difficulty

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
    self.Ready = False
    self.PlayerInfo.lose()

  def win(self):
    self.Ready = False
    self.PlayerInfo.win()

  def addGameLeft(self):
    self.PlayerInfo.addGameLeft()
  
  def reset(self):
    self.Ready = False
    self.PlayerInfo.reset()


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

  def reset(self):
    self.GamesPlayed = 0
    self.GamesLeft = 0
    self.NumberOfWins = 0

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
