# Test Server / Client Communication

import pytest, time, multiprocessing, socket
from .. import server, client

#### Variables and global Server object ###
HOST = '127.0.0.1'
PORT = 5000
# Server object is instantiated outside of test scope as there is no shutdown feature
SERVER = server.CommunicationServer(8)
# Server runs in separate process/thread as it is not asynch / threaded and will otherwise block
Process = multiprocessing.Process(target=SERVER.CreateServer, args=[HOST, PORT])
# Process is set to daemon to be destroyed when main test is complete
Process.daemon = True

### Fixtures ### 

# Server Instances Fixture
# Argument: Maximum number of concurrent users
# Return: List of instantiated CommunicationServer objects
@pytest.fixture
def ServerInstances(MaxConcurrent):
    Instances = []
    for element in MaxConcurrent:
        Instances.append(server.CommunicationServer(element))
    return Instances

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
@pytest.mark.parametrize('MaxConcurrent', [[-50,-10,-5,-1,0,1,5,10,50]])
def test_ServerCapacity(ServerInstances, MaxConcurrent):
    print('\nOutput: ')
    for i in range(len(MaxConcurrent)):
        assert ServerInstances[i].MaxConcurrentClients == MaxConcurrent[i]
        print('Server | Actual: ', str(ServerInstances[i].MaxConcurrentClients), " | ", str(MaxConcurrent[i]))

# Test CreateServer() 
def test_CreateServer():    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ('127.0.0.1', 5000)
    connection_status = sock.connect_ex(addr)
    assert connection_status != 0
    Process.start()
    time.sleep(5)
    connection_status = sock.connect_ex(addr)
    assert connection_status == 0

# Test Client
@pytest.mark.parametrize('NoClients', [8])
def test_Client(ClientInstances, NoClients):
    for client in ClientInstances:
        client.ConnectToServer(HOST,PORT)
    time.sleep(2)
    for client in ClientInstances:
        client.Disconnect()
    
