# Software Engineering and Project Management 1DL251 Fall 2021 Uppsala University - The UU-Game
Repository for Software Engineering and Project Management course at Uppsala University. 
This code belongs to group B and its members:  
Mina Sadat Alemalhoda  
Morten Astrup  
Erik Blomsterberg  
Jennifer Anne Gross  
Robert Paananen  
Samet Burak Türk  
Subhang Vempati  
Laurent Vouriot  
The original component developed by this group was the game engine. The group has also developed their own game platform and uses group C's communication platform.  
The engine uses a minimax algorithm with alpha-beta pruning to find good moves. The heuristics functions are based on this blog: https://kartikkukreja.wordpress.com/2014/03/17/heuristicevaluation-function-for-nine-mens-morris/  
  
### How-to-use: Engine
The engine can be run from the terminal by standing in the src directory and running the command `python3 game_engine.py`.
This will result in the engine reading the current state of the game in the file called board.json and writing the new game state to the file result.json. 
The board.json file contains unsurprisingly a JSON object that describes the current state of the game. There are three difficulties that can be set, these are 'low', 'medium' and 'high'.  
The game engine will always make move for the player that is listed in the file. The player options are 'white' and 'black'.
After each move the engine has made it will increase the turn number by 1. If the engine places a piece it will decrease the amount of pieces left in the hand for the player it made the move for. If the engine manages to get three pieces in a row it will remove one piece from the opponent and decrease their pieces left count by 1. There is a parameter called board size which isn't used by the engine but might be needed by other components wishing to use the engine.  
The last parameter, lines, describes the lines on the board as a list of lists. Each inner list describe one line on the board and what positions are in that line and which player owns that position.
One position can be part of several lines and will therefore be entered in every list describing the lines. If a position has two different owners in different lines the engine might unexectedly crash. It is therefore important that all position that are in multiple lines always have the same owner.  
  
A minimal example of a game state with a board of three lines. Note that position 1,1 is in two lines and has the same owner in both cases.  
{  
    "difficulty": "low",  
    "turn_number": 0,  
    "player_turn": "white",  
    "white_pieces_in_hand": 9,  
    "black_pieces_in_hand": 9,  
    "white_pieces_left": 9,  
    "black_pieces_left": 9,  
    "board_size": 24,  
    "lines": [  
              [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"none"},{"xy":[1,5], "owner":"none"}],  
              [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],  
              [{"xy":[3,3], "owner": "none"},{"xy":[3,4], "owner":"none"},{"xy": [3,5], "owner": "white"}]  
              ]
    }  
      
After the engine has made it move it will mess up the formatting of the file, this does not affect its functionality at all. We recommend to always have a reference board which is never altered but copied to another file when you wish to play a game. This way you always have a clean board for new games.
### Testing
There are currently no tests for the heuristics. The engine and most of its functions are tested. 
To run the tests use the command:
`python3 -m unittest` in the root folder. (Not in the folder src or test)

When creating new test files please use the naming format: test_*.py where * is the thing you're testing.
