from .gamemodel import GameModel, Node, Player, Color
from .utils import clear_screen

class GameView():
    """Represents the view model responsible for rendering a game model to the screen.
    """    
    __model : GameModel
    __left_padding = 6 # in characters
    __top_padding = 0
     
    __msg_buffer : list[str] # buffer for holding messages that the controller wants to display
    """A buffer holding messages that the controller wants to display.\n
    Currently the indices are mapped to conceptually different parts of the UI.\n
    Index 2 is reserved for "notifications" - miscellaneous information to convey to the user when something happens in the game.\n I.e. the user entered an invalid node, the user formed a mill, etc.
    Index 4 is reserved for "action prompts" which are meant to convey to the user what they should do to advance the game.\n
    Other indices are reserved for future expansion.
    """
    __buffer_length = 5

    def __init__(self, model : GameModel):
        self.__msg_buffer = ["" for _ in range(self.__buffer_length)]
        self.__model = model
        self.__model.register_listener(self.draw_board)

    def print_surrender_message(self, surrending_player : Player, winner : Player):
        clear_screen()
        print(f"Player {surrending_player.get_name()} ({surrending_player.color.name}) surrenders!")
        print(f"Player {winner.get_name()} ({winner.color.name}) has won the game!!!")

    def print_win_message(self, winner : Player):
        clear_screen()
        print(f"Player {winner.get_name()} ({winner.color.name}) has won the game!!!")

    def print_draw_message(self):
        clear_screen()
        print("The game ends in a draw!") 

    def node_to_str(self, node : Node) -> str:
        """Converts a given node to string character representation based on the piece at this node.

        Arguments:
            node {Node} ── the node to convert

        Returns:
            str -- the string representation
        """
        if (node.piece == None):
            return " "
        elif (node.piece.owner.color == Color.BLACK):
            return "○"
        elif (node.piece.owner.color == Color.WHITE):
            return "●"

    def __format_phase(self, color : Color):
        player = self.__model.get_player_by_color(color)
        if player is None: return " "
        
        return str(player.get_phase())
    
    def __format_pieces_on_board(self, color : Color):
        player = self.__model.get_player_by_color(color)
        if player is None: return "  "
        pieces_str = str(player.get_active_pieces() - player.get_pieces_to_place())

        if len(pieces_str) > 1:
            return pieces_str
        else:
            return pieces_str + " "

    def __format_pieces_off_board(self, color : Color):
        player = self.__model.get_player_by_color(color)
        if player is None: return "  "
        pieces_str = str(player.get_pieces_to_place())

        if len(pieces_str) > 1:
            return pieces_str
        else:
            return pieces_str + " "

    def set_action_prompt(self, prompt : str):
        self.__msg_buffer[4] = prompt
        self.draw_board()
    
    def clear_action_prompt(self):
        self.__msg_buffer[4] = ""
        self.draw_board()
    
    def set_notification_info(self, info : str):
        self.__msg_buffer[2] = info
        self.draw_board()
    
    def clear_notification_info(self):
        self.__msg_buffer[2] = ""
        self.draw_board()

    def __draw_notification_buffer(self):
        for line in self.__msg_buffer:
            print(line)

    def draw_board(self):
        clear_screen()
        nodes : list[Node] = self.__model.board.get_nodes()
        iter_nodes = iter(map(lambda x: self.node_to_str(x), nodes))

        for i in range(0, self.__top_padding): print("")
        print("     ---------------------------------------- The UU-GAME----------------------------------------")
        print(" "*self.__left_padding,"   0                 1                  2                                                ")
        print(" "*(self.__left_padding+1),next(iter_nodes),"───────────────",next(iter_nodes),"────────────────",next(iter_nodes))
        print(" "*self.__left_padding," │                 │                  │")
        print(" "*self.__left_padding," │    3            │ 4              5 │      " +                                               "           ┌────────────────────────────────────┐")
        print(" "*self.__left_padding," │  ",next(iter_nodes),"───────────",next(iter_nodes),"───────────",next(iter_nodes),"   │                 │            PLAYER BLACK            │")
        print(" "*self.__left_padding," │   │             │              │   │      " +                                               "           │                                    │")
        print(" "*self.__left_padding," │   │             │              │   │      " +                                               "           │  PHASE  : %s                        │"%self.__format_phase(Color.BLACK))
        print(" "*self.__left_padding," │   │      6      │ 7          8 │   │      " +                                               "           │  PIECES ON BOARD  : %s             │"%self.__format_pieces_on_board(Color.BLACK))
        print(" "*self.__left_padding," │   │   ",next(iter_nodes),"──────",next(iter_nodes),"───────",next(iter_nodes),"   │   │                 │  PIECES OFF BOARD : %s             │"%self.__format_pieces_off_board(Color.BLACK))
        print(" "*self.__left_padding," │   │    │                  │    │   │      " +                                               "           │────────────────────────────────────│")
        print(" "*self.__left_padding," │9  │ 10 │ 11               │12  │13 │ 14   " +                                               "           │            PLAYER WHITE            │")
        print(" "*(self.__left_padding+1),next(iter_nodes),"─",next(iter_nodes),"──",next(iter_nodes),"                ",next(iter_nodes),"──",next(iter_nodes),"─",next(iter_nodes),"                │                                    │")
        print(" "*self.__left_padding," │   │    │                  │    │   │      " +                                               "           │  PHASE  : %s                        │"%self.__format_phase(Color.WHITE))
        print(" "*self.__left_padding," │   │    │ 15        16     │ 17 │   │      " +                                               "           │  PIECES ON BOARD   : %s            │"%self.__format_pieces_on_board(Color.WHITE))
        print(" "*self.__left_padding," │   │   ",next(iter_nodes),"──────",next(iter_nodes),"───────",next(iter_nodes),"   │   │                 │  PIECES OFF BOARD  : %s            │"%self.__format_pieces_off_board(Color.WHITE))
        print(" "*self.__left_padding," │   │             │              │   │      " +                                               "           └────────────────────────────────────┘")
        print(" "*self.__left_padding," │   │             │              │   │")
        print(" "*self.__left_padding," │   │   18        │  19          │20 │")
        print(" "*self.__left_padding," │  ",next(iter_nodes),"───────────",next(iter_nodes),"───────────",next(iter_nodes),"   │")
        print(" "*self.__left_padding," │                 │                  │")
        print(" "*self.__left_padding," │  21             │  22              │ 23")
        print(" "*(self.__left_padding+1),next(iter_nodes),"───────────────",next(iter_nodes),"────────────────",next(iter_nodes))
        self.__draw_notification_buffer()
