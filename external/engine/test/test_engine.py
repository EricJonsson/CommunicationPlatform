
import unittest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import reader as file_reader
import board as game_board
from game_engine import Engine
from heuristic import Heuristic
class TestEngine(unittest.TestCase):
    def test_engine_move(self):
        """
        Testing if it is possible to move to a free position
        Expected outcome: A black piece moves from [1,1] to [1,2]. The owner of [1,1] is now 'none'.
        """
        board = game_board.Board("low",0,"black",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}] ])
        engine = Engine(board)
        engine.move_piece((1,1),(1,2),"black")
        old_owner = board.get_owner((1,1))
        new_owner = board.get_owner((1,2))
        
        self.assertEqual(old_owner, "none")
        self.assertEqual(new_owner, 'black')
        # errors
        
    def test_engine_illegal_move_occupied(self):
        """
        Test if it is possible to move to a position that is occupied.
        Expected outcome: The board looks the same after the attempted move has been done.
        """
        board = game_board.Board("low",0,"black",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"white"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}] ])
        engine = Engine(board)
        engine.move_piece((1,1),(1,2),"black")
        old_owner = board.get_owner((1,1))
        new_owner = board.get_owner((1,2))

        self.assertEqual(old_owner, "black")
        self.assertEqual(new_owner, 'white')



    def test_engine_illegal_move_no_exist(self):
        """
        Test if it is possible to move to a position that does not exists.
        Expected outcome: The engine returns the error code False since that position does not exists. The board stays the same as it was before attempting the move.
        """
        board = game_board.Board("low",0,"black",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"white"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}] ])
        engine = Engine(board)
        error_code = engine.move_piece((1,1),(1,4),"black")
        old_owner = board.get_owner((1,1))
        self.assertEqual(error_code, False)
        self.assertEqual(old_owner, "black")
        
        
    def test_engine_all_possible_states_for_place(self):
        """
        Test if engine finds all states for placing on a partially populated board.
        Expected outcome: The engine finds 5 states after white has placed its piece. The first states first line should have a white piece on the second position on the line.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"white"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],
        [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [5,1], "owner": "none"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_place()
        self.assertEqual(len(states),5)
        self.assertEqual(states[0][0][2]['owner'], "white")
                        
    def test_engine_all_possible_states_for_place_empty_board(self):
        """
        Test if engine finds all states for placing on an empty board.
        Expected outcome: The engine finds 7 states after white has placed its piece on the board. 
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "none"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "none"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],
        [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [5,1], "owner": "none"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_place()
        self.assertEqual(len(states),7)
                
    def test_engine_all_possible_states_for_place_full_board(self):
        """
        Testing if engine can handle the case of a full board when placing pieces. 
        Expected outcome: The engine finds no states since the board is already full and no more pieces can be placed.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"white"},{"xy":[1,3], "owner":"white"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "white"}],
        [{"xy":[3,1], "owner": "black"},{"xy":[4,1], "owner":"black"},{"xy": [5,1], "owner": "white"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_place()
        self.assertEqual(len(states),0)

    def test_engine_all_possible_states_for_place_no_board(self):
        """
        Test if engine can handle the case of no boards while placing pieces.
        Expected outcome: The engine finds no states since there is no board to place pieces on.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_place()
        self.assertEqual(len(states),0)

    def test_engine_all_possible_states_for_move(self):
        """
        Test if engine finds all states for moving a piece on a partially populated board.
        Expected outcome: The engine finds 2 states where white has moved its piece one position on each line.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "white"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "white"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],
        [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [5,1], "owner": "none"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_move()
        self.assertEqual(len(states),2)

    def test_engine_all_possible_states_for_move_empty_board(self):
        """
        Test if engine finds all states for moving a piece on a empty board.
        Expected outcome: The engine returns no states since there is no piece to move.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "none"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "none"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],
        [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [5,1], "owner": "none"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_move()
        self.assertEqual(len(states),0)

    def test_engine_all_possible_states_for_move_full_board(self):
        """
        Test if engine finds all states for moving a piece on a full board.
        Expected outcome: The engine returns no states since there is no room to move a piece to.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"white"},{"xy":[1,3], "owner":"white"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "white"}],
        [{"xy":[3,1], "owner": "black"},{"xy":[4,1], "owner":"black"},{"xy": [5,1], "owner": "white"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_move()
        self.assertEqual(len(states),0)

    def test_engine_all_possible_states_for_move_to_intersection(self):
        """
        Tests if it is possible to move to an intersection between two lines.
        Expected outcome: The intersection between line 2 and 3 on position [3,1] will be owned by white. 
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "white"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "white"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],
        [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"white"},{"xy": [5,1], "owner": "black"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_move()
        self.assertEqual(len(states),3)
        self.assertEqual(states[2][1][2]['owner'],"white")
        self.assertEqual(states[2][2][0]['owner'],"white")

    def test_engine_all_possible_states_for_move_no_board(self):
        """
        Tests if the engine can handle no board at all when moving pieces.
        Expected outcome: No moves should be found since there is no board.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_move()
        self.assertEqual(len(states),0)


    def test_engine_all_possible_states_for_remove(self):
        """
        Test for finding all states for removing a piece.
        Expected outcome: 2 states are found.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"black"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "none"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_remove()
        self.assertEqual(len(states),2)

    def test_engine_all_possible_states_for_remove_with_mill(self):
        """
        Test for finding all states for removing a piece with a mill and another piece on the board.
        Expected outcome: 1 state is found since three black pieces form a mill.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"black"},{"xy":[1,3], "owner":"black"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "black"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_remove()
        self.assertEqual(len(states),1)

    def test_engine_all_possible_states_for_remove_with_only_mill(self):
        """
        Test for finding all states for removing a piece with only a mill on the board.
        Expected outcome: 3 states are found since the mill are the only black pieces.
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"black"},{"xy":[1,3], "owner":"black"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "none"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_remove()
        self.assertEqual(len(states),3)

    def test_engine_all_possible_states_for_remove_with_long_mill(self):
        """
        Test for finding all states for removing a piece with a long mill and another piece on the board.
        Expected outcome: 1 state is found since five black pieces form a mill. 
        """
        board = game_board.Board("low",0,"white",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"black"},{"xy":[1,3], "owner":"black"},{"xy":[1,4], "owner":"black"},{"xy":[1,5],"owner":"black"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "black"}]]) 
        engine = Engine(board)
        states = engine.all_possible_states_for_remove()
        self.assertEqual(len(states),1)
        
    def test_engine_all_possible_states_for_jump(self):
        """
        Test for finding all states for moving a piece anywhere on the board.
        Expected outcome: 4 states are found since there are 4 empty positions to move to.
        """
        board = game_board.Board("low",0,"black",12,12,12,12,24,[
        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}]]) 

        
        engine = Engine(board)
        states = engine.all_possible_states_for_jump()

        self.assertEqual(len(states),4)

        
    # def test_minimax(self):
    #     """
    #     Test for the minimax algorithm.
    #     Expected outcome: Finds a good move.
    #     """
    #     r = file_reader.Reader()
    #     r.read('src/board.json')
    #     board = r.board
        
        
if __name__ == '__main__':
    unittest.main()
