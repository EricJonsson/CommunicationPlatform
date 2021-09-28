# CommunicationPlatform
Communications Platform, Group C, Course Software Engineering. 

Used for connecting the UU-GAME components, Gameplatform and GameEngine, together. It enables stable and lightning fast communication, with an easy to use API interface developed by professionals for professionals <sup>TM</sup>. The component is built ontop of the _socketio_ library which allows for an easily extendable library.  

# Installing Dependencies
    python -m pip install -r requirements.txt

# API Reference
All classes with a public interface are described below. 
## CommunicationServer
Class used to run a server / host games. This class is instantiated once, and will run in a separate thread until the main thread exits. 
  ### Attributes:
        MaxConcurrentClients - Maximum number of concurrent users that the server will allow. 
        Clients              - List of all currently connected clients
        ActiveGames          - List of all games currently being played
        TournamentGames      - List of all active tournament games
        ConcludedGames       - List of all games that have finished
  ### Methods:   
  
* CreateServer()
  - Returns: None
  - Parameters: | Integer |
 
        MaxConcurrent - Specify maximum number of concurrent users that the server will allow (Default = 8)
  
## Client
  ### Attributes:
    attribute1
  ### Methods: 
* Method1
  - Returns: None
  - Parameters: | param1 | param2 |
  
        Param1: Desc
        Param2: Desc
* _Player_
  - Attributes:
  - Methods: 
  * ConnectToServer(IP,PORT)
* _Playerinfo_
  
  Used to keep track of all info related to a player. 
  - Attributes: |
      GamesPlayed |
      GamesLeft |
      NumberOfWins |
      
      Keeps track of number of played games, games left in a tournament and number of wins. 
  - Methods: 
* _Game_
  - Attributes:
  - Methods: 

## Tests
    cd tests
    run: pytest
Flags:

    -v for verbose
    -s to enable printing output
  
## License
MIT License
