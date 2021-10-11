from typing import Tuple, List, Dict

from .utils import clear_screen
from .gamemodel import AiDifficulty, GameModel, Board, Player, Color
from .gameview import GameView
from . import gameconfiguration as GameConfig
import json
#from UUgame.engine.core.ai import AI
#from UUgame.engine.api.game_file_adapter import GameFileAdapter


class GameController():
    """
    Represents a game state controller, responsible for manipulating the state of a GameModel and GameView.

    Parameters:
        model {GameModel} -- The model associated with this GameController\n
        view {GameView} -- The view associated with this GameController
    """
    __is_running : bool
    __model : GameModel
    __board : Board
    __view : GameView
    __valid_node_range : List[int]
    __current_player : Player
    __total_turns = 0
    __winning_player = None

    def __init__(self, model : GameModel, view : GameView):
        self.__is_running = False
        self.__total_turns = 0 # sum of all turns taken by all players
        self.__model = model
        self.__view = view
        self.__board = self.__model.board
        self.__valid_node_range = range(0, len(self.__model.board.get_nodes()))
        self.__winning_player = None
        self.__current_player = None
        self.NetworkPlayer = None
        
    def start_game(self) -> Player or None:
        """Starts the game. This is a blocking call.

        Returns:
            Player or None -- the player that won the game, or None if there was a draw.
        """
        self.__is_running = True
        self.__view.draw_board()

        try:
            self.__update()
        except GameAborted as e:
            self.__winning_player = e.winning_player
            self.__view.print_surrender_message(e.aborting_player, self.__winning_player)
        else:
            if self.__winning_player is None:
                self.__view.print_draw_message()
            else:
                self.__view.print_win_message(self.__winning_player)
                
        return self.__winning_player

    def __update(self):
        while self.__is_running:
            self.__current_player = self.__model.get_current_player()
            self.__view.set_action_prompt("It is currently " + self.__current_player.get_name() + "'s turn")
            current_phase = self.__current_player.get_phase()

            if (self.__total_turns // 2) >= GameConfig.MAX_TURNS:
                self.__view.print_draw_message()
                self.__is_running = False
            elif self.__current_player.is_networkplayer():
                self.__handle_networkturn_turn()
            elif self.__current_player.is_ai():
                self.__handle_ai_turn()
            elif current_phase == 1:
                self.__handle_phase_one()
                if self.__phase_one_has_gridlocked():
                    self.__view.print_draw_message()
                    self.__is_running = False
            elif current_phase == 2:
                self.__handle_phase_two()
            elif current_phase == 3:
                self.__handle_phase_three()
            else:
                return
            self.__current_player = self.__advance_turn()
            self.__handle_phase_transition()
            winner = self.__check_winning_player()
            if winner is not None:
                self.__winning_player = winner
                self.__is_running = False

    def __handle_network_turn(self):
        # send and get new game state from AI
        #json_data = self.__model.to_ai_input(self.__current_player)

        while True:
            Messages = self.NetworkPlayer.GetMessageFromOpponent(blocking = True, timeout = 10)
            for message in Messages:
                if 'Gamestate' in message:
                    GameState = message['Gamestate']
                    

        #next_state = AI.next_move(game_file)
        #if next_state is None:
        #    exit(-1)
        #game_file.state = next_state

        #new_json_data : Dict = json.loads(GameFileAdapter.serialize(game_file))

        # load into gamemodel
        self.__model.load_network_output(self.__current_player, GameState)

                
    def __handle_ai_turn(self):
        # send and get new game state from AI
        json_data = self.__model.to_ai_input(self.__current_player)

        #game_file = GameFileAdapter.deserialize(json.dumps(json_data))

        #next_state = AI.next_move(game_file)
        #if next_state is None:
        #    exit(-1)
        #game_file.state = next_state

        #new_json_data : Dict = json.loads(GameFileAdapter.serialize(game_file))

        # load into gamemodel
        #self.__model.load_ai_output(self.__current_player, new_json_data)
    
    def __check_winning_player(self) -> Player or None:
        players = self.__model.get_all_players()

        for player in players:
            if player.get_active_pieces() < 3:
                next_player = players[(players.index(player) + 1) % len(players)]
                return next_player
        return None


    def __handle_phase_one(self):
        self.__handle_placement()

    def __handle_phase_two(self):
        if not self.__player_can_move(self.__current_player):
            return

        has_completed_move = False
        while not has_completed_move:
            selected_node_id = self.__handle_select()
            self.__handle_move(selected_node_id)
            has_completed_move = True

    def __handle_phase_three(self):
        has_completed_move = False
        while not has_completed_move:
            selected_node_id = self.__handle_select()
            self.__handle_move(selected_node_id, ignore_adjacent=True)
            has_completed_move = True

    def __handle_placement(self):
        successful = False
        while not successful:
            self.__view.set_action_prompt(self.__current_player.get_name() + ", enter node to place piece at: ")
            node_id = self.__choose_node() # get node id to place on
            if node_id not in self.__valid_node_range:
                self.__view.set_notification_info("Invalid node!")
                continue

            if self.__board.is_occupied(node_id):
                self.__view.set_notification_info("Node is occupied!")
                continue

            successful = self.__place_piece(node_id)
            self.__current_player.decrement_pieces_to_place()

            if self.__board.is_mill_at(node_id):
                self.__view.set_notification_info(self.__current_player.get_name() + " has formed a mill!")
                self.__handle_remove()

            successful = True        
        self.__view.set_notification_info("")

    def __handle_phase_transition(self):
        players = self.__model.get_all_players()

        for player in players:
            if player.get_active_pieces() == 3:
                player.set_phase(3)
            elif player.get_pieces_to_place() <= 0:
                player.set_phase(2)

    def __handle_remove(self):
        is_valid_remove = False

        while not is_valid_remove:
            self.__view.set_action_prompt(self.__current_player.get_name() + ", enter node to remove from: ")
            node_id = self.__choose_node()
            if not self.__can_remove_at(node_id):
                continue

            owner = self.__board.remove_piece(node_id)
            owner.decrement_active_pieces()
            is_valid_remove = True

    # assumes a valid node_id
    def __can_remove_at(self, node_id) -> bool:
        player_at_node = self.__board.get_node(node_id).occupying_player()
        nodes_occupied_by_player = self.__board.nodes_occupied_by_player(player_at_node)

        if player_at_node is None:
            self.__view.set_notification_info("No piece to remove on that node!")
            return False

        if player_at_node is self.__current_player:
            self.__view.set_notification_info("You can't remove your own pieces!")
            return False

        # does the player have any nodes NOT part of a mill?
        has_non_mill_nodes = len([node_id for node_id in nodes_occupied_by_player if not self.__board.is_mill_at(node_id)]) > 0

        if has_non_mill_nodes and self.__board.is_mill_at(node_id):
            self.__view.set_notification_info("Can't remove mills!")
            return False

        self.__view.set_notification_info("")
        return True

    # returns a selected node (both valid and that has a piece at the node)
    def __handle_select(self) -> int:
        node_id : int
        is_valid_selection = False

        while not is_valid_selection:
            self.__view.set_action_prompt(self.__current_player.get_name() + ", enter node to select piece from: ")
            node_id = self.__choose_node()
            if not self.__board.is_occupied(node_id):
                self.__view.set_notification_info("No piece to select on that node!")
                continue

            if self.__board.get_node(node_id).occupying_player() is not self.__current_player:
                self.__view.set_notification_info("Cannot select other player's pieces!")
                continue
            
            if not self.__board.piece_can_move_to_neighbors(node_id) and self.__current_player.get_phase() < 3:
                self.__view.set_notification_info("That piece has no possible moves!")
                continue
            
            is_valid_selection = True

        self.__view.set_notification_info("")
        return node_id

    def __handle_move(self, from_node_id : int, ignore_adjacent : bool = False):
        is_valid_move = False

        while not is_valid_move:
            self.__view.set_action_prompt(self.__current_player.get_name() + ", enter node to move to: ")
            to_node_id = self.__choose_node()
            if not self.__board.is_occupied(to_node_id) and (self.__board.is_adjacent(from_node_id, to_node_id) or ignore_adjacent):
                self.__board.move_piece_to(from_node_id, to_node_id)

                formed_mill = self.__board.is_mill_at(to_node_id)
                if formed_mill:
                    self.__view.set_notification_info(self.__current_player.get_name() + " has formed a mill!")
                    self.__handle_remove()
                is_valid_move = True
            else:
                self.__view.set_notification_info("Cannot move to node with ID: " + str(to_node_id))
        self.__view.set_notification_info("")

    # always returns a valid node_id
    def __choose_node(self) -> int:
        node_id : int
        is_valid_node = False
        while not is_valid_node:
            node_id = self.__read_input()
            
            if node_id not in self.__valid_node_range:
                self.__view.set_notification_info("Invalid node!")
                continue
            
            is_valid_node = True

        return node_id

    def __phase_one_has_gridlocked(self) -> bool:
        nodes = self.__board.get_nodes()
        for node in nodes:
            if not node.is_occupied():
                return False
        return True

    def __player_can_move(self, player : Player) -> bool:
        nodes_occupied_by_player = self.__board.nodes_occupied_by_player(player)

        for node_id in nodes_occupied_by_player:
            if self.__board.piece_can_move_to_neighbors(node_id):
                return True
        return False


    def __place_piece(self, node_id : int) -> bool:
        if self.__current_player.has_pieces_to_place():
            self.__board.set_piece(node_id, self.__current_player)
            return True
        return False

    def __advance_turn(self) -> Player:
        self.__total_turns += 1
        self.__model.set_turn_count(self.__total_turns // 2)
        self.NetworkPlayer.SendInformationToOpponent({'Gamestate':{self.__model.to_ai_input(self.__current_player)}})
        return self.__model.next_player()

    def __read_input(self) -> str:
        usr_input = input()
        if usr_input.isnumeric():
            return int(usr_input)
        elif self.__is_surrendering(usr_input):
            if self.__confirm_surrender():
                self.__surrender()

    def __is_surrendering(self, str : str) -> bool:
        return str.lower() in ["q", "quit", "surrender", "s"]

    def __confirm_surrender(self) -> bool:
        while True:
            clear_screen()
            print(self.__current_player.get_name() + ", confirm surrender. (Y/N)")
            choice = input().lower()
            if choice == "y":
                return True
            elif choice == "n":
                return False

    def __surrender(self):
        next_player = self.__model.next_player()
        self.__is_running = False
        raise GameAborted(next_player, self.__current_player)

# ugly, but python doesn't have 'great' support for breaking nested loops
class GameAborted(BaseException):
    
    def __init__(self, winning_player : Player or None, aborting_player : Player) -> None:
        super().__init__(winning_player, aborting_player)
        self.winning_player = winning_player
        self.aborting_player = aborting_player
