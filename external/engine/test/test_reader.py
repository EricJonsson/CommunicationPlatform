"""
test_reader.py

Software-engineering project group B

14/09/2021
v0.2

last update : 27/09/21

Laurent VOURIOT
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import reader as file_reader

class TestReader(unittest.TestCase):
    
    def test_read(self):
        reader = file_reader.Reader()
        reader.read("test/test.json")
        board = reader.board
        self.assertEqual(board.get_difficulty(), 'low')
        self.assertEqual(board.get_turn_number(), 0)
        self.assertEqual(board.get_player_turn(), "white")
        self.assertEqual(board.get_white_pieces_in_hand(), 12)
        self.assertEqual(board.get_black_pieces_in_hand(), 12)
        self.assertEqual(board.get_white_pieces_left(), 12) 
        self.assertEqual(board.get_black_pieces_left(), 12)
        self.assertEqual(board.get_board_size(), 24)
        self.assertEqual(board.get_lines(), [
            [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"none"},{"xy":[1,3], "owner":"none"}],
            [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"none"},{"xy": [3,1], "owner": "none"}],
            [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [5,1], "owner": "none"}]
            ])

        # errors
        with self.assertRaises(Exception):
            reader.read("fddsfsdfsdf")

    def test_write(self):
        reader = file_reader.Reader()
        reader.read("test/test.json")
        board = reader.board
        # maybe use the constructor and test setters in another function 
        # values make no sense just to test if setting and writing works
        board.set_difficulty("high")
        board.set_turn_number(1)
        board.set_player_turn("black")
        board.set_white_pieces_in_hand(11)
        board.set_black_pieces_in_hand(11)
        board.set_white_pieces_left(10)
        board.set_black_pieces_left(9)
        board.set_board_size(48)
        board.set_lines([
            [{"xy":[1,3], "owner": "white"},{"xy":[1,5], "owner":"white"},{"xy":[4,3], "owner":"none"}],
            [{"xy":[6,1], "owner": "black"},{"xy":[2,2], "owner":"black"},{"xy": [3,1], "owner": "none"}],
            [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [2,8], "owner": "black"}]
            ])

        reader.write("./test_write.json")

        
        # we read the freshly written json file and verify the values
        reader.read("./test_write.json")
        board = reader.board
        self.assertEqual(board.get_difficulty(), 'high')
        self.assertEqual(board.get_turn_number(), 1)
        self.assertEqual(board.get_player_turn(), "black")
        self.assertEqual(board.get_white_pieces_in_hand(), 11)
        self.assertEqual(board.get_black_pieces_in_hand(), 11)
        self.assertEqual(board.get_white_pieces_left(), 10) 
        self.assertEqual(board.get_black_pieces_left(), 9)
        self.assertEqual(board.get_board_size(), 48)
        self.assertEqual(board.get_lines(), [
            [{"xy":[1,3], "owner": "white"},{"xy":[1,5], "owner":"white"},{"xy":[4,3], "owner":"none"}],
            [{"xy":[6,1], "owner": "black"},{"xy":[2,2], "owner":"black"},{"xy": [3,1], "owner": "none"}],
            [{"xy":[3,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [2,8], "owner": "black"}]
            ])
            
if __name__ == '__main__':
    unittest.main()
