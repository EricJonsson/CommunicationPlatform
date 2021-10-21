"""
reader.py

Software-engineering project group B

14/09/2021
v0.2

last update : 27/09/21 

Group B
"""

import json
import os.path  # exists

from board import Board


class Reader(object):
    """
    Reader class

    reads a json file and create the corresponding board object
    """

    def __init__(self):
        self._board = None

    def read(self, file_name):
        """
        read a json file to create a board object
        :param (string) file_name:
        :return: (Board)
        """

        # check if the path of the file has no errors
        if not os.path.exists(file_name):
            raise OSError("invalid file path")

        # open the file then read the json data in order to create the object
        file = open(file_name, 'r')
        data = json.load(file)
        self._board = Board(data["difficulty"], data["turn_number"], data["player_turn"], 
                            data["white_pieces_in_hand"], data["black_pieces_in_hand"], 
                            data["white_pieces_left"], data["black_pieces_left"],
                            data["board_size"], data["lines"])
        file.close()

    def write(self, file_name):
        """
        write a board into a json file
        :param (string) file_name: file.json
        """
        board_data = { 
                "difficulty": self._board.get_difficulty(),
                "turn_number": self._board.get_turn_number(),
                "player_turn": self._board.get_player_turn(),
                "white_pieces_in_hand": self._board.get_white_pieces_in_hand(),
                "black_pieces_in_hand": self._board.get_black_pieces_in_hand(),
                "white_pieces_left": self._board.get_white_pieces_left(),
                "black_pieces_left": self._board.get_black_pieces_left(),
                "board_size": self._board.get_board_size(),
                "lines":  self._board.get_lines()
                }

        # if file_name doesn't exists, the file is created
        with open(file_name, "w") as json_file:
            json.dump(board_data,json_file, indent=4,separators=(',', ': '))
        json_file.close()
    

    @property
    def board(self):
        """
        :return: (board) property
        """
        return self._board

    def set_board(self, board):
        self._board = board

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    r = Reader()
    try:
        file_name = input("json file name : ")
        r.read(file_name)
    except OSError as oserr:
        print(oserr)



    print(repr(r.board))
