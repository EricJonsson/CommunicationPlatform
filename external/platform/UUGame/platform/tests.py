#from _typeshed import NoneType
import unittest
from .gamemodel import GameModel, Board, Node, Piece, Player, Color
from . import gameconfiguration as GameConfig

# Naming convention for unit tests: test_unitOfWork_stateUnderTest_expectedBehavior (see: The art of unit testing)

# GameModel tests

class TestBoardMethods(unittest.TestCase):

    def test_isAdjacent_NWDiagonal_returnsFalse(self):
        board = Board()
        self.assertFalse(board.is_adjacent(0, 3))
        self.assertFalse(board.is_adjacent(3, 0))
        self.assertFalse(board.is_adjacent(3, 6))
        self.assertFalse(board.is_adjacent(6, 3))

    def test_isAdjacent_NEDiagonal_returnsFalse(self):
        board = Board()
        self.assertFalse(board.is_adjacent(2, 5))
        self.assertFalse(board.is_adjacent(5, 2))
        self.assertFalse(board.is_adjacent(5, 8))
        self.assertFalse(board.is_adjacent(8, 5))

    def test_isAdjacent_SEDiagonal_returnsFalse(self):
        board = Board()
        self.assertFalse(board.is_adjacent(23, 20))
        self.assertFalse(board.is_adjacent(20, 23))
        self.assertFalse(board.is_adjacent(17, 20))
        self.assertFalse(board.is_adjacent(20, 17))

    def test_isAdjacent_SWDiagonal_returnsFalse(self):
        board = Board()
        self.assertFalse(board.is_adjacent(18, 21))
        self.assertFalse(board.is_adjacent(21, 18))
        self.assertFalse(board.is_adjacent(18, 15))
        self.assertFalse(board.is_adjacent(15, 18))

    def test_isAdjacent_bidirectionalCall_alwaysreturnsTrue(self):
        board = Board()
        nodes = board.get_nodes()
        for node in nodes:
            neighbor_ids = board.get_neighbors(node.node_id)
            for neighbor_id in neighbor_ids:
                self.assertTrue(board.is_adjacent(node.node_id, neighbor_id))
                self.assertTrue(board.is_adjacent(neighbor_id, node.node_id))

    def test_getNeighbors_cornerCase_returnsIdOfNeighbors(self):
        board = Board()
        list = board.get_neighbors(0)
        self.assertTrue(1 in list)
        self.assertTrue(9 in list)
        del board

    def test_getNeighbors_twoNeighbours_returnsIdOfNeighbors(self):
        board = Board()
        list = board.get_neighbors(3)
        self.assertTrue(4 in list)
        self.assertTrue(10 in list)
        del board

    def test_getNeighbors_cornerCase_returnsNothingButIdOfNeighbours(self):
        board = Board()
        neighbours = board.get_neighbors(0)
        self.assertFalse(2 in neighbours)
        self.assertFalse(4 in neighbours)
        self.assertFalse(10 in neighbours)
        del board

    def test_getNodes_regularBoard_returnsListOfBoard(self):
        board = Board()
        list_of_nodes = board.get_nodes()
        counter = 0
        for node in list_of_nodes:
            self.assertEqual(node.node_id ,counter)
            counter = counter + 1
        del board

    def test_isValidNode_nodeIsNotValid_ReturnsFalse(self):
        board = Board()
        self.assertFalse(board.is_valid_node(-1))
        self.assertFalse(board.is_valid_node(24))
        del board
    
    def test_isValidNode_nodeIsValid_ReturnsTrue(self):
        board = Board()
        self.assertTrue(board.is_valid_node(0))
        self.assertTrue(board.is_valid_node(5))
        del board

    def test_getNode_nodeIsValid_returnsCorrectNode(self):
        board = Board()
        node = board.get_node(5)
        self.assertEqual(node.node_id, 5)
        del board

    def test_getNode_nodeIsInvalid_returnIsNotNode(self):
        board = Board()
        node = board.get_node(24)
        self.assertNotEqual(type(node), Node)
        del board

    def test_isOccupied_nodeIsFree_returnFalse(self):
        board = Board()
        self.assertFalse(board.is_occupied(0))
        del board

    def test_isOccupied_nodeIsOccupied_returnTrue(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(10, player)
        
        self.assertTrue(board.is_occupied(0))
        self.assertTrue(board.is_occupied(10))
        del board
        del player

    def test_getOccupiedNodes_sixNodesAreOccupied_returnListwithSixNodes(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(1, player)
        board.set_piece(5, player)
        board.set_piece(8, player)
        board.set_piece(14, player)
        board.set_piece(23, player)
        
        list_of_occupied_nodes = board.get_occupied_nodes()
        self.assertEqual(len(list_of_occupied_nodes), 6)
        del board
        del player

    def test_getOccupiedNodes_noNodesAreOccupied_returnEmptyList(self):
        board = Board()
        list_of_occupied_nodes = board.get_occupied_nodes()
        self.assertEqual(len(list_of_occupied_nodes), 0)
        del board

    def test_getOccupiedNodes_sixNodesAreOccupied_returnListwithCorrectSixNodes(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(1, player)
        board.set_piece(5, player)
        board.set_piece(8, player)
        board.set_piece(14, player)
        board.set_piece(23, player)
        
        list_of_occupied_nodes = board.get_occupied_nodes()
        self.assertEqual(list_of_occupied_nodes[0].node_id, 0)
        self.assertEqual(list_of_occupied_nodes[1].node_id, 1)
        self.assertEqual(list_of_occupied_nodes[2].node_id, 5)
        self.assertEqual(list_of_occupied_nodes[3].node_id, 8)
        self.assertEqual(list_of_occupied_nodes[4].node_id, 14)
        self.assertEqual(list_of_occupied_nodes[5].node_id, 23)
        del board
        del player

    def test_setPiece_onePieceIsSet_setsPieceOnCorrectNode(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(8, player)
        node =  board.get_node(8)
        self.assertEqual(node.node_id, 8)
        del board
        del player

    def test_setPiece_EightPiecesAreSet_EightNodesAreOccupied(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(1, player)
        board.set_piece(5, player)
        board.set_piece(9, player)
        board.set_piece(20, player)
        board.set_piece(15, player)
        board.set_piece(3, player)
        board.set_piece(0, player)
        list = board.get_occupied_nodes()
        self.assertEqual(len(list), 7)

        del board
        del player

    def test_removePiece_onePieceIsRemoved_returnsCorrectuser(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(6, player)
        removed = board.remove_piece(6)
        self.assertEqual(removed, player)
        del board
        del player

    def test_removePiece_onePieceIsRemoved_listOfOccupiedIsZero(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(6, player)
        board.remove_piece(6)
        board.remove_piece(0)
        list = board.get_occupied_nodes()
        self.assertEqual(len(list), 0)
        del board
        del player
    
    def test_removePiece_removeEmptyPosition_returnsTypeNone(self):
        board = Board()
        user  = board.remove_piece(0)
        self.assertIsNone(user)
        del board

    def test_isMillAt_millHasNotFormedAtInit_ReturnsFalse(self):
        board = Board()

        for node in board.get_nodes():
            self.assertFalse(board.is_mill_at(node.node_id))
        del board
        
    
    def test_isMillAt_millHasFormedAfterPlacement_ReturnsTrue(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(1, player)
        board.set_piece(2, player)
        self.assertTrue(board.is_mill_at(0))
        self.assertTrue(board.is_mill_at(1))
        self.assertTrue(board.is_mill_at(2))
        del board
        del player

    def test_isMillAt_calledOnInvalidIndex_ReturnsFalse(self):
        board = Board()
        bool = board.is_mill_at(55)
        self.assertFalse(bool)
        del board

    def test_isMillAt_calledOnEmptyPosition_ReturnsFalse(self):
        board = Board()
        bool = board.is_mill_at(5)
        self.assertFalse(bool)
        del board

    def test_isMillAt_aVerticalMillIsCreated_ReturnsTrue(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(2, player)
        board.set_piece(14, player)
        board.set_piece(23, player)
        bool = board.is_mill_at(23)
        self.assertTrue(bool)
        del board
        del player

    def test_isMillAt_aHorizontalMillIsCreated_ReturnsTrue(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(12, player)
        board.set_piece(13, player)
        board.set_piece(14, player)
        bool = board.is_mill_at(13)
        self.assertTrue(bool)
        del board
        del player

    def test_isMillAt_millIsAtAvailablePosition_ReturnsFalse(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(2, player)
        board.set_piece(14, player)
        board.set_piece(23, player)
        bool = board.is_mill_at(3)
        self.assertFalse(bool)
        del board
        del player

    def test_isMillAt_checkMillAtInvalidNode_ReturnsFalse(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(2, player)
        board.set_piece(14, player)
        board.set_piece(23, player)
        self.assertFalse(board.is_mill_at(100))
        del board
        del player

    def test_isMillAt_millIsNotAtNode_ReturnsFalse(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(2, player)
        board.set_piece(14, player)
        board.set_piece(22, player)
        self.assertFalse(board.is_mill_at(2))
        self.assertFalse(board.is_mill_at(14))
        self.assertFalse(board.is_mill_at(22))
        del board
        del player

    def test_isMillAt_millIsNotAtPositionCorner_ReturnsFalse(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(1, player)
        board.set_piece(2, player)
        board.set_piece(14, player)
        self.assertFalse(board.is_mill_at(1))
        self.assertFalse(board.is_mill_at(2))
        self.assertFalse(board.is_mill_at(14))
        del board
        del player

    def test_addMill_sucessfullyAddedAMill_ReturnsTrue(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(1, player)
        board.set_piece(2, player)
        self.assertTrue(board.is_mill_at(0))
        self.assertTrue(board.is_mill_at(1))
        self.assertTrue(board.is_mill_at(2))
        del board

    def test_addMill_doubleAddedAMill_ReturnsFalse(self):
        board = Board()
        player = Player(Color.BLACK)
        board.set_piece(0, player)
        board.set_piece(1, player)
        board.set_piece(3, player)
        self.assertFalse(board.is_mill_at(0))
        self.assertFalse(board.is_mill_at(1))
        self.assertFalse(board.is_mill_at(3))
        del board

class TestGameModelMethods(unittest.TestCase):
    
    def test_getTurnCount_turnCounterIncrements_countEqualsExpected(self):
        model = GameModel()
        model.set_turn_count(-1)
        self.assertEqual(model.get_turn_count(), -1)
        
        model.set_turn_count(200)
        self.assertEqual(model.get_turn_count(), 200)

        del model

    def test_nextPlayer_swapToTheNextPlayer_returnsRightPlayer(self):
        model = GameModel()
        player = model.next_player()
        self.assertEqual(player, model.get_current_player())
        del model

    def test_nextPlayer_swapToTheNextPlayerTwice_returnsFirstPlayer(self):
        model = GameModel()
        current = model.get_current_player()
        player = model.next_player()
        model.next_player()
        self.assertEqual(current, model.get_current_player())
        del model

    def test_nextPlayer_swapToTheNextPlayerTwice_returnsWrongPlayer(self):
        model = GameModel()
        player = model.next_player()
        model.next_player()
        self.assertNotEqual(player, model.get_current_player())
        del model

    def test_setTurnCount_turnCountIsSetTo73_turnCOuntIs73(self):
        model = GameModel()
        model.set_turn_count(73)
        turn = model.get_turn_count()
        self.assertEqual(turn, 73)
        del model

    def test_setTurnCount_turnCountIsSetTo250_turnCountIs250(self):
        model = GameModel()
        model.set_turn_count(250)
        turn = model.get_turn_count()
        self.assertEqual(turn, 250)
        del model

    def test_getTurnCount_turnCountIsSetTo50_turnCountExpectedTo50(self):
        model = GameModel()
        model.set_turn_count(50)
        turn = model.get_turn_count()
        self.assertEqual(turn, 50)
        del model

    def test_getCurrentPlayer_playerIsChecked_initialPlayerExpectedToBeBlack(self):
        model = GameModel()
        player = model.get_current_player()
        self.assertEqual(player.color, Color.BLACK)
        del model

    def test_getCurrentPlayer_playerIsChecked_secondPlayerExpectedToBeWhite(self):
        model = GameModel()
        player1 = Player(Color.BLACK)
        player2 = Player(Color.WHITE)
        model.next_player()
        player = model.get_current_player()
        self.assertEqual(player.color, Color.WHITE)
        del model

    def test_getCurrentPlayer_playerIsChecked_playerExpectedToBeBlack(self):
        model = GameModel()
        player1 = Player(Color.BLACK)
        player2 = Player(Color.WHITE)
        model.next_player()
        model.next_player()
        player = model.get_current_player()
        self.assertEqual(player.color, Color(1))
        del model


class TestNodeMethods(unittest.TestCase):

    def test_isOccupied_testIfOccupied_returnFalse(self):
        node = Node(0)
        bool = node.is_occupied()
        self.assertFalse(bool)
        del node

    def test_isOccupied_testIfOccupied_returnTrue(self):
        node = Node(0)
        player = Player(Color.WHITE)
        piece = Piece(player)
        node.piece = piece
        bool = node.is_occupied()
        self.assertTrue(bool)
        del node
        del piece
        del player
    
    def test_getPiece_getAnExistingPiece_returnThePiece(self):
        node = Node(0)
        player = Player(Color.WHITE)
        piece = Piece(player)
        node.piece = piece
        result = node.get_piece()
        self.assertEqual(result, piece)
        del node    
        del piece
        del player

    def test_getPiece_getANonExistingPiece_returnNone(self):
        node = Node(0)
        result = node.get_piece()
        self.assertEqual(result, None)
        del node    
        
    def test_occupyingPlayer_playerIsOccupying_returnThePlayer(self):
        node = Node(0)
        player = Player(Color.WHITE)
        piece = Piece(player)
        node.piece = piece
        node.piece.owner = player
        result = node.occupying_player()
        self.assertEqual(result, player)
        del node    
        del piece
        del player

    def test_occupyingPlayer_playerIsNotOccupying_returnNone(self):
        node = Node(0)
        player = Player(Color.WHITE)
        piece = Piece(player)
        result = node.occupying_player()
        self.assertEqual(result, None)
        del node    
        del piece
        del player



class TestGamePlayerMethods(unittest.TestCase):
    def test_reset_playerIsReset_playerExpectedToBeReset(self):
        player = Player(Color.BLACK)
        player.set_phase(1)
        player.set_active_pieces(5)
        player.set_pieces_to_place(6)
        player.reset()
        self.assertEqual(player.get_active_pieces(), GameConfig.MAX_PIECES)
        self.assertEqual(player.get_pieces_to_place(), GameConfig.MAX_PIECES)
        self.assertEqual(player.get_phase(), 1)
        
    def test_hasPiecesToPlace_haveActivePieces_playerExpectedToHave4ActivePieces(self): 
        player = Player(Color.BLACK)
        player.set_pieces_to_place(4)
        self.assertEqual(player.has_pieces_to_place(), True)
         
    def test_hasPiecesToPlace_dontHaveActivePieces_playerExpectedToHave4ActivePieces(self): 
        player = Player(Color.BLACK)
        player.set_pieces_to_place(0)
        self.assertEqual(player.has_pieces_to_place(), False)

    def test_getPiecesToPlace_piecesToPlaceAre4_playerExpectedToHave4Pieces(self): 
        player = Player(Color.WHITE)
        player.set_pieces_to_place(4)
        self.assertEqual(player.get_pieces_to_place(), 4) 
           
    def test_getActivePieces_activePiecesAre9_playerExpectedToHave9ActivePieces(self): 
        player = Player(Color.WHITE)
        player.set_active_pieces(9)
        self.assertEqual(player.get_active_pieces(), 9)
    
    def test_decrementPiecesToPlace_decrementPiecesToPlaceTwoTimes_playerExpectedToDecremenTo7(self):
        player = Player(Color.WHITE)
        player.set_pieces_to_place(9)
        player.decrement_pieces_to_place()
        self.assertEqual(player.get_pieces_to_place(), 8) 
        player.decrement_pieces_to_place() 
        self.assertEqual(player.get_pieces_to_place(), 7) 
         
    def test_decrementActivePieces_decrementTwoTimes_playerExpectedToHaveDecrementTwoTimes(self):
        player = Player(Color.WHITE)
        player.set_active_pieces(6)
        player.decrement_active_pieces()
        self.assertEqual(player.get_active_pieces(), 5) 
        player.decrement_active_pieces() 
        self.assertEqual(player.get_active_pieces(), 4) 
    
    def test_getPhase_setPhaseTo4_phaseExpectedToBe4(self):
        player = Player(Color.WHITE)
        player.set_phase(4)
        self.assertEqual(player.get_phase(), 4) 
        
    def test_setPhase_setPhaseTo4ByUsingFunction_phaseExpectedToBe4(self):
        player = Player(Color.WHITE)
        player.set_phase(4)
        self.assertEqual(player.get_phase(), 4) 
        
if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
    input("Press Enter to continue...")