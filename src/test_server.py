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

def delayedSendinformation(client, msg, delay):
    print('Executing delayed message in: ', str(delay), ' seconds')
    time.sleep(delay)
    client.SendInformationToOpponent(msg)
    print('Message sent, exiting thread...')

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

    # Connect Clients to server
    assert Client_1.ConnectToServer(HOST,PORT) == 0
    assert Client_2.ConnectToServer(HOST,PORT) == 0
    # Both Clients Ready up (Should start a match between them)
    Client_1.Ready()
    Client_2.Ready()
    time.sleep(2)
    # Assert that neither client has recieved any messages
    assert len(Client_1.MessageQue) == 0
    assert len(Client_2.MessageQue) == 0
    # Create a thread that sends a message from client 1 to client 2 after 2 seconds
    message = {'Action':'Left','Error':None}
    thread = threading.Thread(target=delayedSendinformation, args=[Client_1,message,2])
    thread.start()

    # Fetch Data and assert that timeout did not occur
    timeout = time.time() + 30
    data_2 = Client_2.GetMessageFromOpponent(blocking = True, timeout = 60)
    assert time.time() < timeout
    data_1 = Client_1.GetMessageFromOpponent(blocking = False)

    # Both Clients should have cleared their message ques after getting messages
    assert len(Client_1.MessageQue) == 0
    assert len(Client_2.MessageQue) == 0

    print('Data 1')
    print(data_1)
    print('Data 2')
    print(data_2)

    # Assert that client 2 has recieved data, and that message was correct
    assert len(data_1) == 0
    assert len(data_2) == 1
    assert data_2[0]['data']['Action'] == 'Left'
    assert data_2[0]['data']['Error'] == None

    # Get messages again, should recieve nothing
    data_1 = Client_1.GetMessageFromOpponent(blocking = False)
    data_2 = Client_2.GetMessageFromOpponent(blocking = False)
    assert len(data_1) == 0
    assert len(data_2) == 0
    
    # Test sending more messages
    msg_1 = {'msg_1':'packet_1'}
    msg_2 = {'msg_2':-1}
    msg_3 = {'msg_3':0.5}
    Client_2.SendInformationToOpponent(msg_1)
    Client_2.SendInformationToOpponent(msg_2)
    Client_2.SendInformationToOpponent(msg_3)
    Client_1.SendInformationToOpponent(msg_1)
    Client_1.SendInformationToOpponent(msg_2)
    time.sleep(1)
    timeout = time.time() + 30
    data_1 = Client_1.GetMessageFromOpponent(blocking = True, timeout = 60)
    assert time.time() < timeout
    data_2 = Client_2.GetMessageFromOpponent(blocking = False)

    print('Data in Client 1: ')
    print(data_1)
    print('Data in Client 2: ')
    print(data_2)
    
    assert len(data_1) == 3
    assert len(data_2) == 2
    assert len(Client_1.MessageQue) == 0
    assert len(Client_2.MessageQue) == 0

    assert data_1[0]['data']['msg_1'] == 'packet_1'
    assert data_1[1]['data']['msg_2'] == -1
    assert data_1[2]['data']['msg_3'] == 0.5
    assert data_2[0]['data']['msg_1'] == 'packet_1'
    assert data_2[1]['data']['msg_2'] == -1
    
    # Test many messages in quick succession
    for i in range(20):
        Client_2.SendInformationToOpponent({'packet':i})

    time.sleep(1)
    
    timeout = time.time() + 30
    data_1 = Client_1.GetMessageFromOpponent(blocking = True, timeout = 60)
    assert time.time() < timeout

    for i in range(20):
        assert data_1[i]['data']['packet'] == i
    
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
