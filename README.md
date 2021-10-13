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
  - Description: Creates and starts a new server
  - Returns: None
  - Parameters: | Integer | String | Integer
 
        MaxConcurrent - The maximum number of concurrent users that the server will allow (Default = 8)

        ip - The host IP-address of the server (Default = '127.0.0.1'/localhost)

        port - The host port of the server (Default = 5000)

* AddAI()
  - Description: Adds an AI player to the Clients list. Fails if the maximumm number of clients have been reached.
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters: | Integer 
        difficulty: The difficulty level of the AI 1-3 (Default = 1)

* GetNumPlayers()
  - Description: Returns the current number of clients.
  - Returns: num_clients

* GetTournamentData()
  - Description: Fetches data about an ongoing tournament
  - Returns: A formatted String listing all current players and their number of wins in order of most to least.

  
* SendToPlayer()
  - Description: Sends a message to the specified player
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters: | String | Dict/String
        name: The name of the player
        info: The info to be sent. Can be a Python Dict or String
  
  
## Player
  ### Attributes:

  ### Event Hooks
  The Player class contains multiple "Event hooks" for reacting to signals sent by the server.  
  The data parameter contains any data sent by the server. Can be a String or Python Dict.  
  The four main ones to consider when intergrating can be found at the top of the ```__callbacks``` method:  
  * game_reset - Fired when the ```CommunicationServer``` calls ```ResetTournament```
  * server_message - Fired when the ```CommunicationServer``` calls ```SendToPlayer```
    data contains the message sent

  * game_info - Fired when the ```CommunicationServer``` adds the player to a new game.

        data contains the following fields:
        opponent: Name of the opponent
        AI: True/False if the opponent is an AI or not
        difficulty: The difficulty level of the opponent (Only applicable if AI = True)

  * gameover - Fired when a ```Player``` calls ```SignalVictory```. 
    The calling ```Player``` is already listening for this event through ```SignalVictory```. But can be extended for the losing opponent.
  

  ### Methods: 
* ConnectToServer 
  - Description: Connects the player to a server
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters: | String | Integer |
  
        ip: The IP-Address of the server that the player is connecting to (Default = '127.0.0.1'/localhost).
        port: The port of the server that the player is connecting to (Default = 5000) 

* Disconnect 
  - Description: Disconnects the player from any connected server
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters:

* SendInformationToOpponent 
  - Description: Sends information to the player's current opponent in a game
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters: | Dictionary/String |
  
        information: The information to be sent to the opponent. Can be a Python Dictionary or String

* RequestStartGame 
  - Description: Sends a request to the server to start a game/tournament (bypasses Ready) 
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters:

* Ready
  - Description: Tells the server that the player is ready to start a game/tournament.  
    Server will automatically start a game/tournament when all players connected are ready.
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters:

* GetMessageFromOpponent 
  - Description: Retrieves all messages sent by the player's opponent since last call.
  - Returns: List
  - Parameters: | Bool | float

        blocking : If True, the method will wait (and block the main thread) for any new messages if there are currently no new messages in the buffer.  
        If False, the method will return and clear the buffer (even if empty). (Default = False)

        timeout: The maximum amount of time the method should wait for new messages if blocking = True.

* SignalVictory
  - Description: Signal the server that a game has concluded and declare the caller as the winner. Optionally pass a parameter with the color of the winning player.
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters: | int |

        winner: The color winning player black = 1, white = 2 (optional).

* GetPlayerInfo 
  - Description: Retrieves `Playerinfo` about the calling player from the server.
  - Returns: Playerinfo

* SetName
  - Description: Sets the name of a player which will be used in tournaments.  
    The name is sent to the server. If a name is already taken, a suffix will be added to the name by the server.
  - Returns: 0 (Success) / -1 (Failure)
  - Parameters: | String |
      name: The requested name


## Playerinfo
  Used to keep track of all info related to a player. 
  - Attributes: |
      GamesPlayed |
      GamesLeft |
      NumberOfWins |
      
      Keeps track of number of played games, games left in a tournament and number of wins. 
  - Methods: 

## Tests
    run: pytest
Flags:

    -v for verbose
    -s to enable printing output
  
## License
MIT License
