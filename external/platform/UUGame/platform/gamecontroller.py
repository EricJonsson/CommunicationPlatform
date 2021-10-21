from typing import Tuple, List, Dict

from .utils import clear_screen
from .gamemodel import AiDifficulty, GameModel, Board, Player, Color
from .gameview import GameView
from . import gameconfiguration as GameConfig
import json
#from UUgame.engine.core.ai import AI
#from UUgame.engine.api.game_file_adapter import GameFileAdapter
from external.engine.src import game_engine, board

def node_lookup(lineid):
    if lineid == [1,1]:
        return 0
    if lineid == [1,4]:
        return 1
    if lineid == [1,7]:
        return 2
    if lineid == [2,2]:
        return 3
    if lineid == [2,4]:
        return 4
    if lineid == [2,6]:
        return 5
    if lineid == [3,3]:
        return 6
    if lineid == [3,4]:
        return 7
    if lineid == [3,5]:
        return 8
    if lineid == [4,1]:
        return 9
    if lineid == [4,2]:
        return 10
    if lineid == [4,3]:
        return 11
    if lineid == [4,5]:
        return 12
    if lineid == [4,6]:
        return 13
    if lineid == [4,7]:
        return 14
    if lineid == [5,3]:
        return 15
    if lineid == [5,4]:
        return 16
    if lineid == [5,5]:
        return 17
    if lineid == [6,2]:
        return 18
    if lineid == [6,4]:
        return 19
    if lineid == [6,6]:
        return 20
    if lineid == [7,1]:
        return 21
    if lineid == [7,4]:
        return 22
    if lineid == [7,7]:
        return 23
    # Node to Line
    if lineid == 0:
        return [1,1]
    if lineid == 1:
        return [1,4]
    if lineid == 2:
        return [1,7]
    if lineid == 3:
        return [2,2]
    if lineid == 4:
        return [2,4]
    if lineid == 5:
        return [2,6]
    if lineid == 6:
        return [3,3]
    if lineid == 7:
        return [3,4]
    if lineid == 8:
        return [3,5]
    if lineid == 9:
        return [4,1]
    if lineid == 10:
        return [4,2]
    if lineid == 11:
        return [4,3]
    if lineid == 12:
        return [4,5]
    if lineid == 13:
        return [4,6]
    if lineid == 14:
        return [4,7]
    if lineid == 15:
        return [5,3]
    if lineid == 16:
        return [5,4]
    if lineid == 17:
        return [5,5]
    if lineid == 18:
        return [6,2]
    if lineid == 19:
        return [6,4]
    if lineid == 20:
        return [6,6]
    if lineid == 21:
        return [7,1]
    if lineid == 22:
        return [7,4]
    if lineid == 23:
        return [7,7]

    return False



class GameController():
    """
    Represents a game state controller, responsible for manipulating the state of a GameModel and GameView.

    Parameters:
        model {GameModel} -- The model associated with this GameController\n
        view {GameView} -- The view associated with this GameController
    """
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
    def start_game(self, NetworkedGame=False) -> Player or None:
        """Starts the game. This is a blocking call.

        Returns:
            Player or None -- the player that won the game, or None if there was a draw.
        """
        self.__is_running = True
        self.__view.draw_board()
        if NetworkedGame:
            self.NetworkPlayer.inGame = True

        try:
            self.__update()
        except GameAborted as e:
            self.__winning_player = e.winning_player
            self.__view.print_win_message(self.__winning_player)
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
                self.__handle_network_turn()
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

        print('Waiting for opponents move...')

        ExitLoop = False
        while not ExitLoop:
            if self.NetworkPlayer.inGame == False:
              next_player = self.__model.next_player()
              self.__is_running = False
              if self.NetworkPlayer.winner == self.__current_player.get_name():
                raise GameAborted(self.__current_player, next_player)
              else:
                raise GameAborted(next_player, self.__current_player)

            Messages = self.NetworkPlayer.GetMessageFromOpponent(blocking = True, timeout = 1)

            for message in Messages:
                if 'Gamestate' in message['data']:
                    GameState = message['data']['Gamestate']
                    ExitLoop = True
                    break
        #next_state = AI.next_move(game_file)
        #if next_state is None:
        #    exit(-1)
        #game_file.state = next_state

        #new_json_data : Dict = json.loads(GameFileAdapter.serialize(game_file))

        # load into gamemodel
        if self.NetworkPlayer.inGame:
            self.__model.load_network_output(self.__current_player, GameState)

                
    def __handle_ai_turn(self):
        # send and get new game state from AI
        json_data = self.__model.to_ai_input(self.__current_player)

        # Placeholder attributes
        ai_difficulty = json_data['ai_difficulty']
        turn_number = 150 - json_data['state']['turns_left']+1
        player_turn = True
        white_pieces_off_board = json_data['state']['we']['pieces_offboard']
        white_pieces_on_board = json_data['state']['we']['pieces_onboard']
        black_pieces_off_board = json_data['state']['they']['pieces_offboard']
        black_pieces_on_board = json_data['state']['they']['pieces_onboard']
        board_size = 24
        
        lines = [[{"xy":[1,1], "owner": "none"},{"xy":[1,4], "owner":"none"},{"xy":[1,7], "owner":"none"}],
                 [{"xy":[2,2], "owner": "none"},{"xy":[2,4], "owner":"none"},{"xy": [2,6], "owner": "none"}],
                 [{"xy":[3,3], "owner": "none"},{"xy":[3,4], "owner":"none"},{"xy": [3,5], "owner": "none"}],
                 [{"xy":[4,1], "owner": "none"},{"xy":[4,2], "owner":"none"},{"xy": [4,3], "owner": "none"}],
                 [{"xy":[4,5], "owner": "none"},{"xy":[4,6], "owner":"none"},{"xy": [4,7], "owner": "none"}],
                 [{"xy":[5,3], "owner": "none"},{"xy":[5,4], "owner":"none"},{"xy": [5,5], "owner": "none"}],
                 [{"xy":[6,2], "owner": "none"},{"xy":[6,4], "owner":"none"},{"xy": [6,6], "owner": "none"}],
                 [{"xy":[7,1], "owner": "none"},{"xy":[7,4], "owner":"none"},{"xy": [7,7], "owner": "none"}],
                 [{"xy":[1,1], "owner": "none"},{"xy":[4,1], "owner":"none"},{"xy": [7,1], "owner": "none"}],
                 [{"xy":[2,2], "owner": "none"},{"xy":[4,2], "owner":"none"},{"xy": [6,2], "owner": "none"}],
                 [{"xy":[3,3], "owner": "none"},{"xy":[4,3], "owner":"none"},{"xy": [5,3], "owner": "none"}],
                 [{"xy":[1,4], "owner": "none"},{"xy":[2,4], "owner":"none"},{"xy": [3,4], "owner": "none"}],
                 [{"xy":[5,4], "owner": "none"},{"xy":[6,4], "owner":"none"},{"xy": [7,4], "owner": "none"}],
                 [{"xy":[3,5], "owner": "none"},{"xy":[4,5], "owner":"none"},{"xy": [5,5], "owner": "none"}],
                 [{"xy":[2,6], "owner": "none"},{"xy":[4,6], "owner":"none"},{"xy": [6,6], "owner": "none"}],
                 [{"xy":[1,7], "owner": "none"},{"xy":[4,7], "owner":"none"},{"xy": [7,7], "owner": "none"}]
                 #[{"xy":[1,1], "owner": "none"},{"xy":[2,2], "owner":"none"},{"xy": [3,3], "owner": "none"}],
#	         [{"xy":[1,7], "owner": "none"},{"xy":[2,6], "owner":"none"},{"xy": [3,5], "owner": "none"}],
#	         [{"xy":[7,1], "owner": "none"},{"xy":[6,2], "owner":"none"},{"xy": [5,3], "owner": "none"}],
#	         [{"xy":[7,7], "owner": "none"},{"xy":[6,6], "owner":"none"},{"xy": [5,5], "owner": "none"}]
        ]

        if ai_difficulty == "easy":
            AI_diff = "low"
        if ai_difficulty == "medium":
            AI_diff = "medium"
        if ai_difficulty == "hard":
            AI_diff = "high"
        
        current_board = board.Board(AI_diff, turn_number, 'white', white_pieces_off_board,black_pieces_off_board,white_pieces_off_board,black_pieces_off_board,24,lines)
        GEngine = game_engine.Engine()
        
        # Place White Pieces
        for piece in json_data['state']['we']['pieces_onboard']:
            node = node_lookup(piece)
            GEngine.place_piece(node,'white',current_board)
        # Place Black Pieces
        for piece in json_data['state']['they']['pieces_onboard']:
            node = node_lookup(piece)
            GEngine.place_piece(node,'black',current_board)
#        print('Board Before: ')
#        print(current_board)
#        input()
        if  ai_difficulty == "easy":
            new_board = GEngine.easy_mode(current_board)
        if ai_difficulty == "medium":
            new_board = GEngine.medium_mode(current_board)
        if ai_difficulty == "hard":
            new_board = GEngine.hard_mode(current_board)
#        print('Board After: ')
#        print(new_board)
#        input()

        print('White Piece Before: ')
        print(json_data['state']['we']['pieces_onboard'])
        print(' ************* ')

        # Gamestate from Board
        black_on_board_updated = []
        white_on_board_updated = []
        for line in new_board.get_lines():
            for item in line:
                #node_keys[str(item['xy'])] = node_lookup(item['xy'])
                if item['owner'] == 'black':
                    node = node_lookup(item['xy'])
                    if not node in black_on_board_updated:
                        black_on_board_updated.append(node)
                if item['owner'] == 'white':
                    node = node_lookup(item['xy'])
                    if not node in white_on_board_updated:
                        white_on_board_updated.append(node)

#        print('White Piece After: ')
#        print(white_on_board_updated)
#        print(' ************* ')
#        input()
        new_json_data = {}
        new_json_data['version'] = 2
        new_json_data['ai_difficulty'] = json_data['ai_difficulty']
        new_json_data['state'] = {}
        new_json_data['state']['turns_left'] = json_data['state']['turns_left'] - 1
        new_json_data['state']['they'] = {}
        new_json_data['state']['they']['pieces_onboard'] = black_on_board_updated
        new_json_data['state']['they']['pieces_offboard'] = black_pieces_off_board
        new_json_data['state']['we'] = {}
        new_json_data['state']['we']['pieces_onboard'] = white_on_board_updated
        if white_pieces_off_board > 0:
            new_json_data['state']['we']['pieces_offboard'] = white_pieces_off_board-1
        else:
            new_json_data['state']['we']['pieces_offboard'] = white_pieces_off_board
        
        # load into gamemodel
        self.__model.load_ai_output(self.__current_player, new_json_data)
    
    def __check_winning_player(self) -> Player or None:
        players = self.__model.get_all_players()

        for player in players:
            if player.get_active_pieces() < 3:
                next_player = players[(players.index(player) + 1) % len(players)]
                return next_player
        return None


    def __sendgamestate(self):
        state = self.__model.to_ai_input(self.__current_player)
        if self.NetworkPlayer != None:
            self.NetworkPlayer.SendInformationToOpponent({'Gamestate':state})

    
    def __handle_phase_one(self):
        self.__handle_placement()
        self.__sendgamestate()
    def __handle_phase_two(self):
        if not self.__player_can_move(self.__current_player):
            self.__sendgamestate()
            return

        has_completed_move = False
        while not has_completed_move:
            selected_node_id = self.__handle_select()
            self.__handle_move(selected_node_id)
            has_completed_move = True
            self.__sendgamestate()

    def __handle_phase_three(self):
        has_completed_move = False
        while not has_completed_move:
            selected_node_id = self.__handle_select()
            self.__handle_move(selected_node_id, ignore_adjacent=True)
            has_completed_move = True
            self.__sendgamestate()

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
