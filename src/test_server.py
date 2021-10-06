# Test Server / Client Communication

import pytest, time, threading, socket
from socketio.client import Client
from socketio.server import Server

import server, client
from server import Client as cs_client 

##### Variables and global Server object #####
HOST = '127.0.0.1'
PORT = 5000
# Server object is instantiated outside of test scope as there is no shutdown feature
SERVER = server.CommunicationServer(8)
SERVER.CreateServer(HOST,PORT)


##### FIXTURES #####

# Client Instances Fixture
# Argument: Number of Clients to create
# Return: List of instantiated Client objects
@pytest.fixture
def ClientInstances(NoClients):
    Instances = []
    for element in range(NoClients):
        Instances.append(client.Player())
    return Instances

def delayedSendinformation(client):
    print('Executing', flush=True)
    time.sleep(2)
    client.SendInformationToOpponent({"data": "Hello dear opponent!"})

def clean_server():
  SERVER.Clients = []
  SERVER.ActiveGames = []
  SERVER.TournamentGames = []
  SERVER.ConcludedGames = []


##### TESTS #####

def test_AI():
  clean_server()

  SERVER.AddAI()
  SERVER.AddAI()
  assert SERVER.GetNumPlayers() == 2

  for i in range(2):
    SERVER.Clients.append(cs_client(str(i)))

  SERVER.generateTournament()
  assert len(SERVER.TournamentGames) == 6

  SERVER.generateRound()

  #Check that AI games are skipped
  assert len(SERVER.ActiveGames) == 1
  assert len(SERVER.ConcludedGames) == 1

  assert SERVER.Clients[0].get_id() != SERVER.Clients[1].get_id()
  #Check that AIs are AI
  assert SERVER.Clients[0].isAI
  assert SERVER.Clients[1].isAI
  #Check that players are not AI
  assert not SERVER.Clients[2].isAI
  assert not SERVER.Clients[3].isAI



#Server unit tests - no events
def test_server_unit():
  clean_server()

  #Fill Clients with dummies
  for i in range(8):
    SERVER.Clients.append(cs_client(str(i)))

  assert SERVER.GetNumPlayers() == 8

  #Try generating a tournament
  SERVER.generateTournament()
  assert len(SERVER.TournamentGames) == 28

  #Try generating a round
  SERVER.generateRound()
  assert len(SERVER.TournamentGames) == 24
  assert len(SERVER.ActiveGames) == 4

  #Test generate new games while tournament is going
  assert SERVER.generateRound() == -1
  assert SERVER.generateTournament() == -1


  #Check all players are in a game
  for i in range(8):
    assert SERVER.FindActiveGameBySid(str(i)) != None

  game = SERVER.FindActiveGameBySid('1')
  opponent = 0

  if(game.PlayerA.get_id() == '1'):
    opponent = game.PlayerB
  else:
    opponent = game.PlayerA

  #Test removing game
  SERVER.ActiveGames.remove(game)

  assert SERVER.FindActiveGameBySid('1') == None
  assert SERVER.FindActiveGameBySid(opponent.get_id()) == None

  for i in range(6):
    SERVER.ActiveGames = []
    assert SERVER.generateRound() == 0
    assert len(SERVER.ActiveGames) == 4

  assert len(SERVER.TournamentGames) == 0

@pytest.mark.parametrize('NoClients', [8])
def test_Tournament_logic(ClientInstances, NoClients):
  clean_server()

  #Connect all clients
  for client in ClientInstances:
    assert client.ConnectToServer(HOST, PORT) == 0

  client0 = ClientInstances[0]
  client0_playerinfo = SERVER.Clients[0].PlayerInfo

  assert client0_playerinfo.GamesLeft == 0
  assert client0_playerinfo.GamesPlayed == 0
  assert client0_playerinfo.NumberOfWins == 0


  #Ready up all players
  for client in ClientInstances:
    assert client.Ready() == 0

  assert client0_playerinfo.GamesLeft == 7

  #Make sure tournament started
  assert len(SERVER.TournamentGames) == 24
  assert len(SERVER.ActiveGames) == 4

  client0.SignalVictory()

  #Check PlayerInfo Updates
  assert client0_playerinfo.GamesLeft == 6
  assert client0_playerinfo.GamesPlayed == 1
  assert client0_playerinfo.NumberOfWins == 1
  

  #Check that game concluded and moved to ConcludedGames
  assert len(SERVER.ActiveGames) == 3
  assert len(SERVER.ConcludedGames) == 1

  client0_game = SERVER.ConcludedGames[0]

  #Get client0 opponent
  opponent = None
  if client0_game.PlayerA == SERVER.Clients[0]:
    opponent = client0_game.PlayerB
  else:
    opponent = client0_game.PlayerA

  opponent_index = SERVER.Clients.index(opponent)
  assert ClientInstances[opponent_index].SignalVictory() == -1

  #Set client0_game as last game
  SERVER.ActiveGames = []
  SERVER.ActiveGames.append(client0_game)
  client0_game.Active = True

  #Check if client_0 wins on disconnect
  assert ClientInstances[opponent_index].Disconnect() == 0
  time.sleep(0.5)

  assert client0_playerinfo.GamesLeft == 5
  assert client0_playerinfo.GamesPlayed == 2
  assert client0_playerinfo.NumberOfWins == 2

  #Check that players can retrieve their player info
  playerinfo = client0.GetPlayerInfo()
  assert playerinfo is not None
  assert playerinfo['GamesLeft'] == 5
  assert playerinfo['GamesPlayed'] == 2
  assert playerinfo['NumberOfWins'] == 2

  #Check if new round started when last game concluded
  assert len(SERVER.TournamentGames) == 20
  assert len(SERVER.ActiveGames) == 4

  for client in ClientInstances:
        client.Disconnect()

# Test Client Matching and Sending Data
@pytest.mark.parametrize('NoClients', [8])
def test_ClientMessaging(ClientInstances, NoClients):
    clean_server()

    Client_1 = ClientInstances[0]
    Client_2 = ClientInstances[1]

    GameState = {'Data':'Message','Error':None}

    assert Client_1.ConnectToServer(HOST,PORT) == 0
    assert Client_2.ConnectToServer(HOST,PORT) == 0

    Client_1.Ready()
    Client_2.Ready()
    time.sleep(2)

    thread = threading.Thread(target=delayedSendinformation, args=[Client_1])
    thread.start()


    data_2 = Client_2.GetMessageFromOpponent(blocking = True, timeout = 60)

    thread.join()
    
    #assert len(data_1) == 0
    assert len(data_2) > 0
    
    #assert data['Data'] == 'Message'
    #assert data['Error'] == None

    for client in ClientInstances:
        client.Disconnect()
    
# Test Client Connections and Server Capacity
@pytest.mark.parametrize('NoClients', [16])
def test_ClientConnect(ClientInstances, NoClients):
    clean_server()
    # List of indices in ClientInstances list
    Set = [0,1,2,3,4,5,6,7]
    for i in Set:
        # Assert that client connection attempt returns 0
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == 0
    time.sleep(0.1)
    # Check that server has 8 clients connected
    assert len(SERVER.Clients) == 8

    Set = [8,9,10,11]
    for i in Set:
        # Assert that client connection attempt returns -1
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == -1
    time.sleep(0.1)
    # Check that server did not connect any more clients
    assert len(SERVER.Clients) == 8

    Set = [0,1,2,3]
    for i in Set:
        ClientInstances[i].Disconnect()
    time.sleep(0.1)
    # Check that server registered 4 client disconnects
    assert len(SERVER.Clients) == 4

    Set = [8,9,10,11]
    for i in Set:
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == 0
    time.sleep(0.1)
    assert len(SERVER.Clients) == 8

    # Assert client connection failed & capacity = 8
    assert ClientInstances[12].ConnectToServer(HOST,PORT) == -1
    assert SERVER.MaxConcurrentClients == 8
    # Increment server capacity by 2
    SERVER.MaxConcurrentClients += 2
    time.sleep(0.1)
    # Check that capacity was incremented
    assert SERVER.MaxConcurrentClients == 10
    # Assert that two more clients can connect, but fail on third
    assert ClientInstances[12].ConnectToServer(HOST,PORT) == 0
    assert ClientInstances[13].ConnectToServer(HOST,PORT) == 0
    assert ClientInstances[14].ConnectToServer(HOST,PORT) == -1
    time.sleep(0.1)
    # Check that server has 10 clients connected
    assert len(SERVER.Clients) == 10
    # Disconnect 2 Clients
    ClientInstances[12].Disconnect()
    ClientInstances[13].Disconnect()
    # Decrement server capacity
    SERVER.MaxConcurrentClients -= 2
    time.sleep(0.1)
    assert SERVER.MaxConcurrentClients == 8
    time.sleep(0.1)
    assert len(SERVER.Clients) == 8

    # Disconnect all clients
    for client in ClientInstances:
        client.Disconnect()
    # Final Sleep to allow disconnections to finalize
    time.sleep(0.1)
