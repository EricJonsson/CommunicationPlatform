"""
board.py

Software-engineering project group B

14/09/2021
v0.2

last_update : 27/09/21 

Laurent VOURIOT

"""


class Board(object):
    """
    the board class

    a board in a certain state of the game
    """
    def __init__(self, difficulty, turn_number, player_turn, white_pieces_in_hand,
                 black_pieces_in_hand, white_pieces_left, black_pieces_left,
                 board_size, lines):
        """se
        constructor
        
        # TODO discuss about the representation of difficulty
        :param: difficulty (int) : 1 low, 2 medium, 3 high
        :param: turn_number (int) 
        :param: player_turn (bool) : True white, False black
        :param: white_pieces_in_hand (int)
        :param: black_pieces_in_hand (int)
        :param: white_pieces_left (int)
        :param: black_pieces_left (int)
        :param: board_size (int)
        :param: lines (list(list))
        """

        self._difficulty = difficulty
        self._turn_number = turn_number
        self._player_turn = player_turn
        self._white_pieces_in_hand = white_pieces_in_hand
        self._black_pieces_in_hand = black_pieces_in_hand
        self._white_pieces_left = white_pieces_left
        self._black_pieces_left = black_pieces_left
        self._board_size = board_size
        self._lines = lines
        self._value = 0



# GETTERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_turn_number(self):
        return self._turn_number
    def get_player_turn(self):
        return self._player_turn
    
    def get_difficulty(self):
        return self._difficulty

    def get_turn_number(self):
        return self._turn_number

    def get_lines(self):
        return self._lines

    def get_board_size(self):
        return self._board_size

    def get_black_pieces_left(self):
        return self._black_pieces_left

    def get_white_pieces_left(self):
        return self._white_pieces_left
    
    def get_black_pieces_hand(self):
        return self._black_pieces_in_hand

    def get_white_pieces_hand(self):
        return self._white_pieces_in_hand

    def get_white_pieces_in_hand(self): 
        return self._white_pieces_in_hand

    def get_black_pieces_in_hand(self): 
        return self._black_pieces_in_hand

    def get_value(self):
        return self._value
        
    def get_owner(self, position):
        x,y = position
        for line in self._lines:
            position = next((item for item in line if item["xy"] == [x,y]), None) #Finds the position and its owner if it exists.
            if position: return position['owner']
        return "none"
    def get_player_pieces_in_hand(self, player):
        if player == 'white': return self._white_pieces_in_hand
        else: return self._black_pieces_in_hand
    
    # SETTERS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_value(self, value):
        self._value = value
    def set_player_turn(self, player_turn):
        self._player_turn = player_turn
    
    def set_difficulty(self, difficulty):
        self._difficulty = difficulty

    def set_turn_number(self, turn_number):
        self._turn_number = turn_number

    def set_lines(self, lines):
        self._lines = lines

    def set_board_size(self, board_size):
        self._board_size = board_size

    def set_black_pieces_left(self, black_pieces_left):
        self._black_pieces_left = black_pieces_left

    def set_white_pieces_left(self, white_pieces_left):
        self._white_pieces_left = white_pieces_left

    def set_white_pieces_in_hand(self, white_pieces_in_hand): 
        self._white_pieces_in_hand = white_pieces_in_hand

    def set_black_pieces_in_hand(self, black_pieces_in_hand): 
        self._black_pieces_in_hand = black_pieces_in_hand

    def increase_turn_number(self):
        self._turn_number += 1
    def __repr__(self):
        """
        :return: string to show all the attributes of the board for debug
        """
        return "difficulty : {}\n" \
               "turn number: {}\n" \
               "player_turn : {}\n" \
               "white in hand {}\n" \
               "black in hand {}\n" \
               "white left {}\n" \
               "black left {}\n" \
               "size {}\n".format(self._difficulty,
                                  self._turn_number,
                                   self._player_turn,
                                   self._white_pieces_in_hand,
                                   self._black_pieces_in_hand,
                                   self._white_pieces_left,
                                   self._black_pieces_left,
                                   self._board_size)



