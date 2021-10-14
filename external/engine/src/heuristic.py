import sys
import os
import json
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import os.path  # 
from collections import defaultdict
from board import Board
from collections import Counter

#going to analyze everything with the more positive number being a better move for black; 
#negative better for white.

class Heuristic():

    #I originally planned to weight things with arrasy but decided it may not be needed. TBD
    def createVertexArray(board):
        # vertexArray = np.zeros(board.board_size,board.board_size)
        #print(board)
        #vertexArray = [board.get_board_size(),board.get_board_size()]
        #myArray = [board.get_board_size(),board.get_board_size()]
        w, h = board.get_board_size(), board.get_board_size()
        myArray = [[0 for x in range(w)] for y in range(h)]
        for line in board._lines:
            for item in line:
                x,y = item["xy"]
                myArray[x][y] += 1
        return myArray
    
    
    #This isn't checking for all three in a row, it should only be checking the newest piece for 3 in a row
    def numberOfMorris(self, board):
        score = 0
        for line in board.get_lines():
            numinrow =0
            last = ""
            for item in line:
                if (last == item["owner"]):
                    numinrow +=1
                else :
                    numinrow = 0
                if item["owner"] == "black":
                    if numinrow == 2:
                        score = score + 1
                elif item["owner"] == "white":
                    if numinrow == 2:
                        score = score - 1
                last = item["owner"]  
        return score
    
    def numberOfPieces(self, board):
        score = board.get_black_pieces_left() - board.get_white_pieces_left()
        return score
        
    def closedMorris(self, board, previous_board):
        if self.check_n_in_a_row(previous_board, board, 'white', 3):
            return -1
        if self.check_n_in_a_row(previous_board, board, 'black', 3):
            return 1
        return 0
    
    def numberTwoPiece(self,board):
        score = 0
        for line in board.get_lines():
            numinrow =0
            last = ""
            found_three = False
            for item in line:
                if (last == item["owner"]):                        
                        if item["owner"] == "black":
                            score = score + 1 - found_three
                        elif item["owner"] == "white":
                            score = score - 1 + found_three
                    
                last = item["owner"]  
        return score
    
    def numberThreePiece(self, board):
        score = 0
        lines = board.get_lines()
        all_twos = []
        for line in lines:
            numinrow =0
            last_owner = ""
            last_item = None
            pos_to_add = []
            for item in line:
                if (last_owner != 'none' and last_owner == item["owner"]):
                    pos_to_add = [last_item, item]
                    numinrow += 1
                last_owner = item["owner"]
                last_item = item
            if numinrow == 1:
                all_twos += pos_to_add
                
        for item in all_twos:
            if all_twos.count(item) == 2:
                all_twos.remove(item)
                if item['owner'] == 'white': score -= 1
                else: score +=1
        return score
        
    def doubleMorris(self, board):
        score = 0
        all_morrises = []
        for line in board.get_lines():
            numinrow =0
            last_owner = ""
            last_item = None
            pos_to_add = []
            for item in line:
                if (last_owner != 'none' and last_owner == item["owner"]):
                    numinrow +=1
                    pos_to_add.append(last_item)
                else:
                    numinrow = 0
                if numinrow == 2:
                    pos_to_add.append(item)
                    all_morrises+=pos_to_add
                    numinrow = 0
                last_owner = item["owner"]
                last_item = item
        for item in all_morrises:
            if all_morrises.count(item) >= 2:
                all_morrises.remove(item)
                if item['owner'] == 'white': score -= 1
                else: score +=1
        return score

        
    def winningState(self, board):
        score = 0
        if board.get_black_pieces_left() == 2:
            score = -1
        if board.get_white_pieces_left() == 2:
            score = 1
        return score
    
    
#This will check for each spot of one color and identify if it is blocked in.  It will make the value negative if black is blocked in.
    def findEachBlockedPiece(self, board):
        block_list = []
        for line in board.get_lines():
            for x, item in enumerate(line):
                blocked = False
                try:
                    if x == 0 and line[x+1]['owner'] != 'none':
                        block_list.append(item)
                        continue
                except: None
                try:
                    if line[x-1]['owner'] != 'none':
                        blocked = True
                    else:
                        continue
                except: None
                try:
                    if line[x+1]['owner'] != 'none':
                        blocked = True
                    else:
                        blocked = False
                except: None
                if blocked: block_list.append(item)
        count = 0
        for item in block_list:
            if block_list.count(item) > 1:
                if item['owner'] == 'white':count += 1
                else: count -= 1
            block_list.remove(item)
        return count
    
    """
    This function calculates several heuristics in the same loop iterations to avoid traversing the list so many times. To understand the heuristic functions better please examine the functions above instead as they are essentially the same, just not bunched together into one loop.
    """
    def firstPhaseLoops(self, board):
        lines = board.get_lines()
        block_list = []
        tp_all_twos = []
        nm_score = 0
        twp_score = 0
        for line in lines:
            tp_numinrow =0
            tp_last_owner = ""
            tp_last_item = None
            tp_pos_to_add = []
            nm_numinrow =0
            nm_last = ""
            twp_numinrow =0
            twp_last = ""
            found_two = False

            for x, item in enumerate(line):
                 blocked = False
                 try:
                     if x == 0 and line[x+1]['owner'] != 'none':
                         block_list.append(item)
                         continue
                 except: None
                 try:
                     if line[x-1]['owner'] != 'none':
                         blocked = True
                     else:
                         continue
                 except: None
                 try:
                     if line[x+1]['owner'] != 'none':
                         blocked = True
                     else:
                         blocked = False
                 except: None
                 if blocked: block_list.append(item)


                 if (tp_last_owner != 'none' and tp_last_owner == item["owner"]):
                    tp_pos_to_add = [tp_last_item, item]
                    tp_numinrow += 1
                 tp_last_owner = item["owner"]
                 tp_last_item = item

                 if (nm_last == item["owner"]):
                    nm_numinrow +=1
                 else :
                    nm_numinrow = 0
                 if item["owner"] == "black":
                    if nm_numinrow == 2:
                        nm_score = nm_score + 1
                 elif item["owner"] == "white":
                    if nm_numinrow == 2:
                        nm_score = nm_score - 1
                 nm_last = item["owner"]

                 if (twp_last == item["owner"]):                        
                        if item["owner"] == "black":
                            twp_score = twp_score + 1 - found_two * 2
                            found_two = True
                        elif item["owner"] == "white":
                            twp_score = twp_score - 1 + found_two * 2
                            found_two = True
                 twp_last = item["owner"]  
    

                 
            if tp_numinrow == 1:
                tp_all_twos += tp_pos_to_add

            
                 
        blocked_count = 0
        tp_count = 0
        for item in block_list:
            if block_list.count(item) >= 2:
                if item['owner'] == 'white':blocked_count += 1
                else: blocked_count -= 1
                block_list.remove(item)
            
        for item in tp_all_twos:
            if tp_all_twos.count(item) == 2:
                tp_all_twos.remove(item)
                if item['owner'] == 'white': tp_count -= 1
                else: tp_count +=1
        return blocked_count + 7 * tp_count + 26 * nm_score + 10*twp_score

#This calls the other functions and adds a weight toeach one unique for first phase. .  
    def firstPhaseState(self, board, previous_board):
       score = 0
       score = 9 * self.numberOfPieces(board)  + self.firstPhaseLoops(board)
       if previous_board:
           score += 18 * self.closedMorris(board, previous_board)
       return score


#This calls the other functions and adds a weight toeach one unique for first phase. .  

    def secondPhaseState(self, board, previous_board):
        score = 0
        score = 10 * self.findEachBlockedPiece(board) + 1086* self.winningState(board) + 11 * self.numberOfPieces(board) + 43 * self.numberOfMorris(board) + 8*self.doubleMorris(board) + 14 * self.closedMorris(board, previous_board)
        return score

    def thirdPhaseState(self, board, previous_board):
        score = 16 * self.closedMorris(board, previous_board) + 10 * self.numberTwoPiece(board) + self.numberThreePiece(board) + 1190 * self.winningState(board)
        return score
    
    def check_n_in_a_row(self, previous_board, current_board, current_player_color,n):
        if not previous_board: return 0
        for xIndex, line in enumerate(previous_board.get_lines()):
            for yIndex, item in enumerate(line):
                 if item['owner'] != current_board.get_lines()[xIndex][yIndex]['owner']:
                     if self.n_in_row(current_board, item['xy'], current_player_color,n):
                         return 1
        return 0
 
        
#this function checks for n in a row at a given poisition for a given player color
#it should only be called through check_three_in)a_row to check the latest player move.
    def n_in_row(self, board, position, current_player_color,n):        
        for line in board.get_lines():
            numinrow =0
            hasPosition = 0
            for item in line:
                if (current_player_color == item["owner"]):
                    numinrow +=1
                if (position == item['xy']):
                    hasPosition = 1
                if ((hasPosition == 1) and (numinrow == n)):
                    return 1
        return 0


#simple testing boards for Jenn
#board = Board("low",0,"black",12,10,12,10,24,[
#        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"white"},{"xy":[1,3], "owner":"none"}],
#        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"white"},{"xy": [3,1], "owner": "none"}] ])

#board2 = Board("low",0,"black",12,12,12,12,24,[
#        [{"xy":[1,1], "owner": "black"},{"xy":[1,2], "owner":"black"},{"xy":[1,3], "owner":"black"}],
#        [{"xy":[1,1], "owner": "black"},{"xy":[2,1], "owner":"black"},{"xy": [3,1], "owner": "black"}] ])
