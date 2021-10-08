from gamemodel import GameModel, Board, Node, Player
from gamecontroller import GameController
from gameview import GameView

game_model : GameModel
game_view : GameView
game_controller : GameController

def main():
    game_model = GameModel()
    game_view = GameView(game_model)
    game_controller = GameController(game_model, game_view)

    start_game_phase2(game_model, game_view, game_controller)
    input("Press Enter to continue...")


def start_game_phase2(game_model : GameModel, game_view : GameView, game_controller : GameController):
    players : list[Player] = game_model.get_all_players()

    black = players[0]
    white = players[1]

    #set up black player
    black.set_pieces_to_place(0)
    black.set_active_pieces(9)
    black.set_phase(2)
    
    #set up white player
    white.set_pieces_to_place(0)
    white.set_active_pieces(9)
    white.set_phase(2)
    
    
    # set the pieces
    game_model.board.set_piece(0, white)
    game_model.board.set_piece(3, white)
    game_model.board.set_piece(5, black)
    game_model.board.set_piece(6, white)
    game_model.board.set_piece(7, white)
    game_model.board.set_piece(8, white)
    game_model.board.set_piece(9, black)
    game_model.board.set_piece(10, white)
    game_model.board.set_piece(11, black)
    game_model.board.set_piece(12, white)
    game_model.board.set_piece(13, black)
    game_model.board.set_piece(16, black)
    game_model.board.set_piece(17, white)
    game_model.board.set_piece(18, black)
    game_model.board.set_piece(19, black)
    game_model.board.set_piece(20, black)
    game_model.board.set_piece(21, white)
    game_model.board.set_piece(22, black)

    game_model.set_turn_count(24)

    # check that black has mills
    assert(game_model.board.is_mill_at(5))
    assert(game_model.board.is_mill_at(13))
    assert(game_model.board.is_mill_at(16))
    assert(game_model.board.is_mill_at(18))
    assert(game_model.board.is_mill_at(19))
    assert(game_model.board.is_mill_at(20))
    assert(game_model.board.is_mill_at(22))

    # check that white has mills
    assert(game_model.board.is_mill_at(0))
    assert(game_model.board.is_mill_at(3))
    assert(game_model.board.is_mill_at(6))
    assert(game_model.board.is_mill_at(7))
    assert(game_model.board.is_mill_at(8))
    assert(game_model.board.is_mill_at(12))
    assert(game_model.board.is_mill_at(17))

    game_controller.start_game()

if __name__ == "__main__":
    main()