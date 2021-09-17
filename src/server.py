# Communication Platform - Server

# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer: # External
  Clients = []
  MaxConcurrentClients = 1
  
class ClientConnectionInfo:
  port = 1
