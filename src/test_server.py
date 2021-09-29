# Test Server / Client Communication

import pytest, time, multiprocessing, socket
import server, client

#### Variables and global Server object ###
HOST = '127.0.0.1'
PORT = 5000
# Server object is instantiated outside of test scope as there is no shutdown feature
SERVER = server.CommunicationServer(8)
SERVER.CreateServer(HOST,PORT)
time.sleep(1)

### Fixtures ### 

# Server Instances Fixture
# Argument: Maximum number of concurrent users
# Return: List of instantiated CommunicationServer objects


#@pytest.fixture
#def ServerInstances(MaxConcurrent):
#    Instances = []
#    for element in MaxConcurrent:
#        Instances.append(server.CommunicationServer(element))
#    return Instances

# Client Instances Fixture
# Argument: Number of Clients to create
# Return: List of instantiated Client objects
@pytest.fixture
def ClientInstances(NoClients):
    Instances = []
    for element in range(NoClients):
        Instances.append(client.Player())
    return Instances

# Test Server Capacity
#@pytest.mark.parametrize('MaxConcurrent', [[-50,-10,-5,-1,0,1,5,10,50]])
#def test_ServerCapacity(ServerInstances, MaxConcurrent):
#    print('\nOutput: ')
#    for i in range(len(MaxConcurrent)):
#        assert ServerInstances[i].MaxConcurrentClients == MaxConcurrent[i]
#        print('Server | Actual: ', str(ServerInstances[i].MaxConcurrentClients), " | ", str(MaxConcurrent[i]))

# Test CreateServer() 
def test_CreateServer():    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ('127.0.0.1', 5000)
    connection_status = sock.connect_ex(addr)
    assert connection_status == 0

# Test Client
@pytest.mark.parametrize('NoClients', [12])
def test_Client(ClientInstances, NoClients):
    Connected = []
    Disconnected = ClientInstances
    
    for i in range(8):
        assert ClientInstances[i].ConnectToServer(HOST,PORT) == 0
        Connected.append(ClientInstances[i])
        time.sleep(1)
    Disconnected = ClientInstances[:8]
    assert len(SERVER.Clients) == 8


    for i in range(4):
        assert Disconnected[i].ConnectToServer(HOST,PORT) == -1
        time.sleep(1)

    
    for client in Connected:
        client.Disconnect()
    
