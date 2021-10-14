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
This function will move a piece and return the new lines, if no moves were found it returns false.
"""
def move_piece(self, start, end, player_color, lines):
        moves = []
        for line in lines:
            start_item = None
            end_item = None
            for item in line:
                if item['xy'] == start:
                    start_item = item
                if item['xy'] == end:
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


