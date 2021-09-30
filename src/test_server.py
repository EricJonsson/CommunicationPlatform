# Test Server / Client Communication

import pytest, time, multiprocessing, socket
import server, client

##### Variables and global Server object #####
HOST = '127.0.0.1'
PORT = 5000
# Server object is instantiated outside of test scope as there is no shutdown feature
SERVER = server.CommunicationServer(8)
SERVER.CreateServer(HOST,PORT)
time.sleep(1)


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


##### TESTS #####

# Test Client Matching and Sending Data
@pytest.mark.parametrize('NoClients', [8])
def test_ClientMatching(ClientInstances, NoClients):

    Client_1 = ClientInstances[0]
    Client_2 = ClientInstances[1]

    GameState = {'Data':'Message','Error':None}

    assert Client_1.ConnectToServer(HOST,PORT) == 0
    assert Client_2.ConnectToServer(HOST,PORT) == 0

    Client_1.Ready()
    Client_2.Ready()
    time.sleep(2)
    
    Client_1.SendInformationToOpponent(GameState)
    time.sleep(2)


    data_2 = Client_2.GetMessageFromOpponent()
    print('*** Data Recieved on client 2 ***')
    print(data_2)
    print('****************************')
    data_1 = Client_1.GetMessageFromOpponent()
    print('*** Data Recieved on client 1 ***')
    print(data_1)
    print('****************************')
    
    assert data['Data'] == 'Message'
    assert data['Error'] == None

    for client in ClientInstances:
        client.Disconnect()
    
# Test Client Connections and Server Capacity
@pytest.mark.parametrize('NoClients', [16])
def test_ClientConnect(ClientInstances, NoClients):

    # List of indices in ClientInstances list
    Set = [0,1,2,3,4,5,6,7]
    for i in Set:
        # Assert that client connection attempt returns 0
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == 0
    time.sleep(1)
    # Check that server has 8 clients connected
    assert len(SERVER.Clients) == 8

    Set = [8,9,10,11]
    for i in Set:
        # Assert that client connection attempt returns -1
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == -1
    time.sleep(1)
    # Check that server did not connect any more clients
    assert len(SERVER.Clients) == 8

    Set = [0,1,2,3]
    for i in Set:
        ClientInstances[i].Disconnect()
    time.sleep(1)
    # Check that server registered 4 client disconnects
    assert len(SERVER.Clients) == 4

    Set = [8,9,10,11]
    for i in Set:
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == 0
    time.sleep(1)
    assert len(SERVER.Clients) == 8

    # Assert client connection failed & capacity = 8
    assert ClientInstances[12].ConnectToServer(HOST,PORT) == -1
    assert SERVER.MaxConcurrentClients == 8
    # Increment server capacity by 2
    SERVER.MaxConcurrentClients += 2
    time.sleep(1)
    # Check that capacity was incremented
    assert SERVER.MaxConcurrentClients == 10
    # Assert that two more clients can connect, but fail on third
    assert ClientInstances[12].ConnectToServer(HOST,PORT) == 0
    assert ClientInstances[13].ConnectToServer(HOST,PORT) == 0
    assert ClientInstances[14].ConnectToServer(HOST,PORT) == -1
    time.sleep(1)
    # Check that server has 10 clients connected
    assert len(SERVER.Clients) == 10
    # Disconnect 2 Clients
    ClientInstances[12].Disconnect()
    ClientInstances[13].Disconnect()
    # Decrement server capacity
    SERVER.MaxConcurrentClients -= 2
    time.sleep(1)
    assert SERVER.MaxConcurrentClients == 8
    time.sleep(1)
    assert len(SERVER.Clients) == 8

    # Disconnect all clients
    for client in ClientInstances:
        client.Disconnect()
    # Final Sleep to allow disconnections to finalize
    time.sleep(2)

