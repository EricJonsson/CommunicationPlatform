from board import Board
from reader import Reader
from heuristic import Heuristic
import copy
import os
import sys
class Engine(object):
    """
    Engine class
    
    Takes a board and manipulates it
    """

    def __init__(self,board = None):
        self._board = board
        self._all_first_boards = []

    """
    This function will place a piece, if the board hasn't changed it will return false. 
    """
    def place_piece(self, position, player_color, board):
        lines = board.get_lines()
        lines_before = copy.deepcopy(lines)
        for line in lines:
            for item in line:
                if item['xy'] == position and item['owner'] == 'none':
                    item['owner'] = player_color

        return not lines == lines_before

    
    """
    Arguments: (start_x, start_y), (end_x, end_y), player color
    Returns: The updated lines where the piece has moved
    Moves a piece for player_color from the starting position to the end position.
    Color should be either 'white' or 'black'
    Example: move_piece((1,1),(1,2),"white") returns
    """
    def move_piece(self, start, end, player_color, lines = None):
        if not lines: lines = self._board.get_lines()
        start_x, start_y = start
        end_x, end_y = end
        moves = []
        for line in lines:
            start_item = None
            end_item = None
            for item in line:
                if item['xy'] == [start_x, start_y]:
                    start_item = item
                if item['xy'] == [end_x, end_y]:
                    end_item = item
            if start_item and end_item and start_item != end_item and start_item['owner'] == player_color and end_item['owner'] == 'none':
                moves.append([start_item,end_item])

        if not moves: return False

        for line in lines:
            for item in line:
                for move in moves:
                    if item['xy'] == move[1]['xy']: item['owner'] = player_color
                    elif item['xy'] == move[0]['xy']: item['owner'] = 'none'

        return lines


    
    """
    Arguments: list of lists containing the lines for a board, player color
    Returns: A list of lists of lists containing every possible placement of a piece as a seperate game state.

    Finds all positions that are free and returns a list of the new states for each found position.
    If no lines or player color is provided the function will use the current state of the board.

    Example: all_possible_states_for_place([[{"xy":[1,1], "owner":"none"},{"xy":[1,2], "owner":"none"}]] retruns 
    [
     [ <- start state 1
      [{'xy': [1, 1], 'owner': 'white'}, {'xy': [1, 2], 'owner': 'none'}] <- line on the board
     ], <- end state 1
     [ <- start state 2
      [{'xy': [1, 1], 'owner': 'none'}, {'xy': [1, 2], 'owner': 'white'}] <- line on the board
     ] <- end state 2
    ]
 
    """
    def all_possible_states_for_place(self, lines = None, player_color = None):
        if not lines: lines = self._board.get_lines()
        if not player_color: player_color = self._board.get_player_turn()
        free_positions = []
        for line in lines:
            free_positions += (item.copy() for item in line if item["owner"] == "none" and item not in free_positions)
        all_states = []
        for pos in free_positions:
            new_lines = []
            pos['owner'] = player_color
            for line in lines:
                new_lines.append([pos if (pos['xy'] == item['xy']) else item for item in line])
            
            all_states.append(new_lines)
        return all_states

    """
    Arguments: list of lists containing the lines for a board, player color
    Returns: A list of lists of lists containing every possible jump for a piece as a seperate game state.
    
    """
    def all_possible_states_for_jump(self, lines = None, player_color = None):
        if not lines: lines = self._board.get_lines()
        if not player_color: player_color = self._board.get_player_turn()
        all_states_for_place = self.all_possible_states_for_place(lines, player_color)
        items = []
        all_states = []
        for y,line in enumerate(lines):
            for x, item in enumerate(line):
                if item['owner'] == player_color and item not in items:
                    items.append(item)

        for org_item in items:
            local_states = copy.deepcopy(all_states_for_place)
            for lines in local_states:
                for line in lines:
                    for item in line:
                        if item['xy'] == org_item['xy']: item['owner'] = 'none'
            all_states += local_states
        return all_states
    """
    Arguments: list of lists containing the lines for a board, player color
    Returns: A list of lists of lists containing every possible move of a piece as a seperate game state.
    
    Finds all possible pieces that can be removed and returns a new state for each removed piece.
    Example: 
    """
    def all_possible_states_for_move(self, lines= None, player_color = None):
        if not lines: lines = self._board.get_lines()
        if not player_color: player_color = self._board.get_player_turn()
        lines_local = copy.deepcopy(lines)
        all_states = []
        for line in lines_local:
            for index, item in enumerate(line):
                if(item['owner'] == player_color):                   
                    if index != 0 and index != len(line)-1:
                        before = line[index - 1]
                        after = line[index + 1]
                        if(before['owner'] == 'none'):
                            ret_val = self.move_piece(tuple(item['xy']),tuple(before['xy']),player_color,copy.deepcopy(lines_local))
                            if not ret_val: return ret_val
                            all_states.append(ret_val)
                        if(after['owner'] == 'none'):
                            ret_val = self.move_piece(tuple(item['xy']),tuple(after['xy']),player_color,copy.deepcopy(lines_local))
                            if not ret_val: return ret_val
                            all_states.append(ret_val)
                    elif index == 0 and len(line) > 1:
                        after = line[index + 1]
                        if(after['owner'] == 'none'):
                            ret_val = self.move_piece(tuple(item['xy']),tuple(after['xy']),player_color,copy.deepcopy(lines_local))
                            if not ret_val: return ret_val
                            all_states.append(ret_val)
                    elif index == len(line) -1:
                        before = line[index - 1]
                        if(before['owner'] == 'none'):
                            ret_val = self.move_piece(tuple(item['xy']),tuple(before['xy']),player_color,copy.deepcopy(lines_local))
                            if not ret_val: return ret_val
                            all_states.append(ret_val)
        return all_states


    
    """
    Arguments: list of lists containing the lines for a board, player color
    Returns: A list of lists of lists containing every possible removal of piece as a seperate game state.
    
    """
    def all_possible_states_for_remove(self, lines = None, player_color = None):
        if not lines: lines = self._board.get_lines()
        if not player_color: player_color = self._board.get_player_turn()
        lines_local = copy.deepcopy(lines)
        all_positions = []
        all_states = []
        other_player_color = ""
        if player_color == 'white': other_player_color = 'black'
        else: other_player_color = 'white'
        for line in lines_local:
            for index, item in enumerate(line):
                if(item['owner'] != player_color and item['owner'] != 'none' and item not in all_positions and not self.three_in_row(lines, item['xy'], other_player_color, True)):
                    all_positions.append(item.copy())

        if not all_positions:
            for line in lines_local:
                for index, item in enumerate(line):
                    if(item['owner'] != player_color and item['owner'] != 'none' and item not in all_positions):
                        all_positions.append(item.copy())

        for pos in all_positions:
            pos['owner'] = 'none'
            new_lines = []
            for line in lines:
                new_lines.append([pos if (pos['xy'] == item['xy']) else item for item in line])
            all_states.append(new_lines)
        return all_states
    
    """
    Arguments: depth, maximizing player color, first iteration (bool), board, alpha value, beta value, board from the previus iteration
    Returns: The best value for the maximizing player
    Note: This is a recursive function that runs until depth is 0. The parameter first determines if the function is in its first call or if it has been recursivly called. Please set first to True when calling this function from elsewhere. This function will update the list _all_first_boards with all the possible next moves the engine function found.
    """
    def minimax(self,depth, max_player, first, board, a, b, previous_board=None):
        heur = Heuristic()
        if (depth == 0):            
            if max_player == 'black':
                if board.get_black_pieces_hand() > 0:
                    return heur.firstPhaseState(board, previous_board)
                elif board.get_black_pieces_left() == 3:
                    return heur.thirdPhaseState(board, previous_board)
                else:
                    return heur.secondPhaseState(board, previous_board)
            else:
                if board.get_white_pieces_hand() > 0:
                    return heur.firstPhaseState(board, previous_board)
                elif board.get_white_pieces_left() == 3:
                    return heur.thirdPhaseState(board, previous_board)
                else:
                    return heur.secondPhaseState(board, previous_board)
                    
        if max_player == 'white':                
            value = float('inf')
            if board.get_white_pieces_hand() > 0:
                all_states = self.all_possible_states_for_place(board.get_lines(), 'white')
                for lines in all_states:
                    new_board = Board(board.get_difficulty(), board.get_turn_number(), 'black', board.get_white_pieces_hand()-1, board.get_black_pieces_hand(), board.get_white_pieces_left(),board.get_black_pieces_left(),board.get_board_size(), lines)
                    if self.check_three_in_a_row(board, new_board, 'white'):
                        new_board = self.minimax_remove(new_board, 'white')

                    value = min(value, self.minimax(depth-1, 'black', False, new_board,a,b, board))
                    if(first):
                        new_board.set_value(value)
                        self._all_first_boards.append(new_board)
                    if value <= a:
                        break
                    b = min(b,value)
                        
                return value
            elif board.get_white_pieces_left() == 3:
                all_states = self.all_possible_states_for_jump(board.get_lines(), 'white')
                for lines in all_states:
                    new_board = Board(board.get_difficulty(), board.get_turn_number(), 'black', board.get_white_pieces_hand(), board.get_black_pieces_hand(), board.get_white_pieces_left(),board.get_black_pieces_left(),board.get_board_size(),lines)
                    if self.check_three_in_a_row(board, new_board, 'white'):
                        new_board = self.minimax_remove(new_board, 'white')
    
                    value = min(value, self.minimax(depth-1, 'black', False, new_board,a,b, board))
                    if(first):
                        new_board.set_value(value)
                        self._all_first_boards.append(new_board)
                    if value <= a:
                        break
                    b = min(b,value)
                return value
            else:
                all_states = self.all_possible_states_for_move(board.get_lines(), 'white')
                for lines in all_states:
                    new_board = Board(board.get_difficulty(), board.get_turn_number(), 'black', board.get_white_pieces_hand(), board.get_black_pieces_hand(), board.get_white_pieces_left(),board.get_black_pieces_left(),board.get_board_size(),lines)
                    if self.check_three_in_a_row(board, new_board, 'white'):
                        new_board = self.minimax_remove(new_board, 'white')
    
                    value = min(value, self.minimax(depth-1, 'black', False, new_board,a,b, board))
                    if(first):
                        new_board.set_value(value)
                        self._all_first_boards.append(new_board)
                    if value <= a:
                        break
                    b = min(b,value)

                return value
        if max_player == 'black':
            value = float('-inf')
            if board.get_black_pieces_hand() > 0:
                all_states = self.all_possible_states_for_place(board.get_lines(), 'black')
                for lines in all_states:
                    new_board = Board(board.get_difficulty(),board.get_turn_number(), 'white', board.get_white_pieces_hand(), board.get_black_pieces_hand()-1, board.get_white_pieces_left(),board.get_black_pieces_left(),board.get_board_size(),lines)
                    if self.check_three_in_a_row(board, new_board, 'black'):                        
                        new_board = self.minimax_remove(new_board, 'black')

                    value = max(value, self.minimax(depth-1, 'white', False, new_board,a,b, board))
                    if(first):
                        new_board.set_value(value)
                        self._all_first_boards.append(new_board)
                    if value >= b:
                        break
                    a = max(a,value)

                return value
            elif board.get_black_pieces_left() == 3:
                all_states = self.all_possible_states_for_jump(board.get_lines(), 'black')
                for lines in all_states:
                    new_board = Board(board.get_difficulty(), board.get_turn_number(), 'white', board.get_white_pieces_hand(), board.get_black_pieces_hand(), board.get_white_pieces_left(),board.get_black_pieces_left(),board.get_board_size(),lines)
                    if self.check_three_in_a_row(board, new_board, 'black'):
                        new_board = self.minimax_remove(new_board, 'black')
    
                    value = max(value, self.minimax(depth-1, 'white', False, new_board,a,b, board))
                    if(first):
                        new_board.set_value(value)
                        self._all_first_boards.append(new_board)
                    if value >= b:
                        break
                    a = max(a, value)

                return value
            else:
                all_states = self.all_possible_states_for_move(board.get_lines(), 'black')
                
                for lines in all_states:
                    new_board = Board(board.get_difficulty(), board.get_turn_number(), 'white', board.get_white_pieces_hand(), board.get_black_pieces_hand(), board.get_white_pieces_left(),board.get_black_pieces_left(),board.get_board_size(),lines)
                    if self.check_three_in_a_row(board, new_board, 'black'):
                        new_board = self.minimax_remove(new_board, 'black')

                    value = max(value, self.minimax(depth-1, 'white', False, new_board,a,b, board))
                    if(first):
                        new_board.set_value(value)
                        self._all_first_boards.append(new_board)
                    if value >= b:
                        break
                    a = max(a, value)
                return value
    """
    Arguments: a board, player color
    Returns: a board where player color has removed on of the opponents pieces.
    This function finds a good piece to remove from the opponents and removes it from the board.
    """
    def minimax_remove(self,board, max_player):
        heur = Heuristic()
        value = 0
        if max_player == 'white': value = float('inf')
        else: value = float('-inf')
        best_board = board
        all_states = self.all_possible_states_for_remove(board.get_lines(), max_player)
        for lines in all_states:
            if max_player == 'white':
                new_board = Board(board.get_difficulty(),board.get_turn_number(), 'black', board.get_white_pieces_hand(), board.get_black_pieces_hand(), board.get_white_pieces_left(),board.get_black_pieces_left()-1,board.get_board_size(),lines)
                new_value = heur.secondPhaseState(new_board,board)
                if new_value < value:
                    value = new_value
                    best_board = new_board
            else:
                new_board = Board(board.get_difficulty(), board.get_turn_number(),'white', board.get_white_pieces_hand(), board.get_black_pieces_hand(), board.get_white_pieces_left()-1,board.get_black_pieces_left(),board.get_board_size(),lines)
                new_value = heur.secondPhaseState(new_board, board)
                if new_value > value:
                    value = new_value
                    best_board = new_board
        return best_board

    """
    Arguments: player color
    Returns: The board with the highest or lowest value, depending on the player.
    This function gets the best board for the chosen player from the list _all_first_boards.
    This function should be called after the minimax funtion is done to ensure that the list is updated with all
    new possible moves
    """
    def get_best_board(self,player):
        if not self._all_first_boards:
            return False
        best_board = self._all_first_boards[0]
        for board in self._all_first_boards:
            if player == 'white':

                if board.get_value() < best_board.get_value():
                    best_board = board
            else:
                if board.get_value() > best_board.get_value():
                    best_board = board
        self._all_first_boards = []
        best_board.increase_turn_number()
        return best_board

    """
    check the last state to the current state for the move and see if there is a new three in a row for the current player color.
    note: this is expecting the game state to only have the most recent move added.

    """
    def check_three_in_a_row(self, previous_board, current_board, current_player_color):
        if not previous_board: return 0
        for x_index, line in enumerate(previous_board.get_lines()):
            for y_index, item in enumerate(line):
                 if item['owner'] != current_board.get_lines()[x_index][y_index]['owner']:
                     if self.three_in_row(current_board.get_lines(), item['xy'], current_player_color):
                         return 1
        return 0
 
        
    def three_in_row(self, lines, position, current_player_color, for_remove = False):
        for line in lines:
            num_in_row = 0
            has_position = 0
            already_three = False
            for index, item in enumerate(line):
                if (current_player_color == item["owner"]) and already_three:
                    return 0
                elif already_three:
                    return 1
                elif current_player_color == item['owner']:
                    num_in_row += 1
                else:
                    has_position = 0
                if (position == item['xy'] and item['owner'] == current_player_color):
                    has_position = 1
             
                if ((has_position == 1) and (num_in_row == 3)):
                    already_three = True
                    if index == len(line)-1: return 1
                    if for_remove: return 1
                    
                if has_position and num_in_row > 3 and for_remove:
                    return 1
        return 0
    

    def easy_mode(self, board):
        depth = 2
        player = board.get_player_turn()
        self.minimax(depth, player, True, board, float('-inf'),float('inf'))
        board_new = self.get_best_board(player)
        if not board_new:
            board.increase_turn_number()
            if player == 'white': board.set_player_turn('black')
            else: board.set_player_turn('white')
            return board
        return board_new

    def medium_mode(self, board):
        depth = 3
        player = board.get_player_turn()
        self.minimax(depth, player, True, board, float('-inf'),float('inf'))
        board_new = self.get_best_board(player)
        if not board_new:
            board.increase_turn_number()
            if player == 'white': board.set_player_turn('black')
            else: board.set_player_turn('white')
            return board
        return board_new
    
    def hard_mode(self, board):
        depth = 4
        player = board.get_player_turn()
        self.minimax(depth, player, True, board, float('-inf'),float('inf'))
        board_new = self.get_best_board(player)
        if not board_new:
            board.increase_turn_number()
            if player == 'white': board.set_player_turn('black')
            else: board.set_player_turn('white')
            return board
            
        return board_new
    
def main():
    r = Reader()
    try:
        file_name = "board.json"
        r.read(file_name)
        board = r.board
        diff = board.get_difficulty()
        e = Engine()
        if diff == 'low':
            board = e.easy_mode(board)
        if diff == 'medium':
            board = e.medium_mode(board)
        if diff == 'high':
            board = e.hard_mode(board)

        r.set_board(board)
        r.write("result.json")
    except OSError as oserr:
        print(oserr)


if __name__ == "__main__":
    main()
   # cProfile.run('main()')
  
