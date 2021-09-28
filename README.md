# CommunicationPlatform
Communications Platform, Group C, Course Software Engineering. 

Used for connecting the UU-GAME components, Gameplatform and GameEngine, together. It enables stable and lightning fast communication, with an easy to use API interface developed by professionals for professionals <sup>TM</sup>. The component is built ontop of the _socketio_ library which allows for an easily extendable library.  

## Installing Dependencies
python -m pip install -r requirements.txt

## API Reference
### Classes
 CommunicationServer
* CommunicationServer
  - Attributes:
  - Methods: 
* Client
  - Attributes:
  - Methods: 
* Player
  - Attributes:
  - Methods: 
* Playerinfo
  - Desc: Used to keep track of all info related to a player. 
  - Attributes: |
      GamesPlayed |
      GamesLeft |
      NumberOfWins |
      
      Keeps track of number of played games, games left in a tournament and number of wins. 
  - Methods: 
* Game
  - Attributes:
  - Methods: 

## Tests
cd tests
run: pytest

flags: 
  - -v for verbose
  - -s to enable printing output
  
## License
MIT License
