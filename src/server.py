# Communication Platform - Server

# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer: # External
  Clients = []
  MaxConcurrentClients = 1
  
class ClientConnectionInfo:
  port = 1
  
class Client:
  Socket = None
  PlayerInfo = None
  
class PlayerInfo:
  GamesPlayed = 0
  GamesLeft = 0
  NumberOfWins = 0
  # Send the PlayerInfo to the player via the Socket
  def SendStatistics()
    pass
