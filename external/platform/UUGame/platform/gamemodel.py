from enum import Enum, IntEnum
from typing import Tuple, List, Dict
from .utils import StateObservable
from . import gameconfiguration as GameConfig


class Direction(IntEnum):
    NORTH = 0
    NORTH_EAST = 1
    EAST = 2
    SOUTH_EAST = 3
    SOUTH = 4
    SOUTH_WEST = 5
    WEST = 6
    NORTH_WEST = 7

# Matrix for defining edges and the direction of those edges. Do NOT use or manipulate outside this module.
# element order: [N, NE, E, SE, S, SW, W, NW]
_directed_adjacency_matrix = [
                                                       #node_id
    [None, None, 1, None, 9, None, None, None],        #0
    [None, None, 2, None, 4, None, 0, None],           #1
    [None, None, None, None, 14, None, 1, None],       #2
    [None, None, 4, None, 10, None, None, None],       #3
    [1, None, 5, None, 7, None, 3, None],              #4
    [None, None, None, None, 13, None, 4, None],       #5
    [None, None, 7, None, 11, None, None, None],       #6
    [4, None, 8, None, None, None, 6, None],           #7
    [None, None, None, None, 12, None, 7, None],       #8
    [0, None, 10, None, 21, None, None, None],         #9
    [3, None, 11, None, 18, None, 9, None],            #10
    [6, None, None, None, 15, None, 10, None],         #11
    [8, None, 13, None, 17, None, None, None],         #12
    [5, None, 14, None, 20, None, 12, None],           #13
    [2, None, None, None, 23, None, 13, None],         #14
    [11, None, 16, None, None, None, None, None],      #15
    [None, None, 17, None, 19, None, 15, None],        #16
    [12, None, None, None, None, None, 16, None],      #17
    [10, None, 19, None, None, None, None, None],      #18
    [16, None, 20, None, 22, None, 18, None],          #19
    [13, None, None, None, None, None, 19, None],      #20
    [9, None, 22, None, None, None, None, None],       #21
    [19, None, 23, None, None, None, 21, None],        #22
    [14, None, None, None, None, None, 22, None]       #23
    ]

class Color(IntEnum):
    NONE = 0
    BLACK = 1
    WHITE = 2

class AiDifficulty(IntEnum):
    NONE = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3

    def __str__(self):
        return self.name.lower()


class Player(StateObservable):
    """
    Represents the state of a player.

    Parameters:
        color {Color} -- The color that the player should have.

    Attributes:
        color {Color} -- The player's color.
    """
    color : Color
    __phase = 1
    __active_pieces : int # the total amount of pieces remaining in the game for this player
    __pieces_to_place : int # the amount of pieces the player has left to place on the board
    __max_pieces : int = GameConfig.MAX_PIECES # maximum amount of pieces that the player can have in the game
    __name : str
    __is_ai : bool # might need a reference to an ai controller object instead
    __ai_difficulty : AiDifficulty
    __is_networkplayer : bool

    def __init__(self, color : Color, name : str = ""):
        super().__init__()
        self.color = color
        self.__active_pieces = self.__max_pieces
        self.__pieces_to_place = self.__max_pieces
        self.__name = name
        self.__is_ai = False
        self.__ai_difficulty = AiDifficulty.NONE

    def is_ai(self) -> bool:
        """Returns whether or not this player is controlled by an AI.

        Returns:
            bool -- True if this player is controlled by an AI. Otherwise False.
        """        
        return self.__is_ai
    
    def enable_ai(self, ai_difficulty : AiDifficulty = AiDifficulty.EASY):  
        """Enables AI for this player.

        Keyword Arguments:
            ai_difficulty {AiDifficulty} -- the new difficulty of this AI player (default: {AiDifficulty.EASY})
        """           
        self.__is_ai = True
        self.__ai_difficulty = ai_difficulty
    
    def disable_ai(self):
        """Disables AI for this player.
        """        
        self.__is_ai = False
        self.__ai_difficulty = AiDifficulty.NONE
    
    def set_ai_difficulty(self, new_difficulty : AiDifficulty):
        """Sets the AI difficulty for this player.

        Arguments:
            new_difficulty {AiDifficulty} -- the new ai difficulty
        """
        self.__ai_difficulty = new_difficulty

    def get_ai_difficulty(self) -> AiDifficulty:
        """Gets the AI difficulty of this player.

        Returns:
            AiDifficulty -- the ai difficulty of this player
        """        
        return self.__ai_difficulty

    def get_name(self) -> str:
        """Gets the name of the player.

        Returns:
            str -- the name of the player
        """        
        return self.__name
    
    def set_name(self, new_name : str):
        """Sets a new name for this player.

        Arguments:
            new_name {str} -- the new name of the player
        """        
        self.__name = new_name
        self.trigger_state_event()

    def get_max_pieces(self) -> int:
        """Gets the maximum number of pieces that this player can have on the board.

        Returns:
            int -- the maximum number of pieces for this player
        """        
        return self.__max_pieces

    def reset(self):
        """Resets the player state to its starting state.

        This is equivalent to creating a new player object without changing its color.
        """
        self.__phase = 1
        self.__active_pieces = GameConfig.MAX_PIECES
        self.__pieces_to_place = GameConfig.MAX_PIECES

    def has_pieces_to_place(self) -> bool:
        """Returns whether or not the player has pieces left to place.

        Returns:
            bool -- True if the player has pieces left to place. Otherwise False.
        """
        return self.__pieces_to_place > 0

    def get_pieces_to_place(self) -> int:
        """Gets the number of pieces that the player has left to place.

        Returns:
            int -- The amount of pieces left to place for this player.
        """
        return self.__pieces_to_place

    def set_pieces_to_place(self, nr_of_pieces : int):
        """Sets the number of pieces that this player is able to place onto the board.

        Arguments:
            nr_of_pieces {int} -- the number of pieces
        """
        self.__pieces_to_place = nr_of_pieces
        self.trigger_state_event()

    def get_active_pieces(self) -> int:
        """Returns the number of active pieces that this player has in the game.
        This is the total number of pieces that the player still has active in the game.
        This also includes pieces that the player has yet to place on the board.

        Returns:
            int -- The amount of active pieces.
        """
        return self.__active_pieces

    def set_active_pieces(self, nr_of_pieces : int):
        """Sets the number of pieces that this player has left in the game.
        This is the total number of pieces that the player still has active in the game.
        This also includes pieces that the player has yet to place on the board.

        Arguments:
            nr_of_pieces {int} -- the number of active pieces
        """
        self.__active_pieces = nr_of_pieces
        self.trigger_state_event()

    def decrement_pieces_to_place(self):
        """Decrements the amount of pieces that the player can place.
        """
        self.set_pieces_to_place(self.get_pieces_to_place()-1)

    def decrement_active_pieces(self):
        """Decrements the total amount of pieces that the player has left in the game.
        This also includes pieces that the player has yet to place on the board
        """
        self.set_active_pieces(self.get_active_pieces()-1)

    def get_phase(self) -> int:
        """Gets the current phase that the player is in.

        Returns:
            int -- The current phase.
        """
        return self.__phase

    def set_phase(self, new_phase : int) -> None:
        """Sets the current phase of the player.

        Arguments:
            new_phase {int} -- the new phase for the player
        """
        self.__phase = new_phase
        self.trigger_state_event()

class Piece():
    """
    Represents the state of a piece.

    Parameters:
        owner {Player} -- The player owner of this piece.

    Attributes:
        owner {Player} -- The player owner of this piece.
    """
    owner : Player

    def __init__(self, owner : Player):
        self.owner = owner

    def __eq__(self, other):
        if other == None:
            return False
        return self.owner is other.owner

class Node():
    """
    Represents the state of a node.

    Parameters:
        node_id {int} -- The node id for this node.

    Attributes:
        node_id {int} -- The node id for this node.\n
        piece {Piece} -- The occupying this node. May be None.
    """
    node_id = -1
    piece : Piece

    def __init__(self, node_id):
        self.node_id = node_id
        self.piece = None

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.node_id == other.node_id

    def __hash__(self) -> int:
        return hash(self.node_id)

    def is_occupied(self) -> bool:
        '''Check if this node is occupied by a player.

        Returns:
            bool -- True if occupied, else False
        '''
        return self.piece != None

    def get_piece(self) -> Piece or None:
        '''Gets the piece at this node.

        Returns:
            Piece or None -- The piece at the node if there is a piece at the node, otherwise returns None
        '''
        return self.piece

    def occupying_player(self) -> Player or None:
        '''Gets the player occupying this node.

        Returns:
            Player or None -- If a player occupies this node, return that player, else return None
        '''
        if self.piece == None:
            return None
        return self.piece.owner


# Subject to interface change
class Board(StateObservable):
    """
    Represents the state of a board.
    """
    __graph: List[Node]
    __mills: List[List[Node]]

    def __init__(self):
        super().__init__()
        self.__graph = [Node(n) for n in range(24)]
        self.__mills = []

    def get_neighbors(self, node_id : int) -> List[int]:
        '''Get adjacently connected nodes from a given node ID.

        Arguments:
            node_id {int} -- The node ID to get adjacent nodes from.

        Returns:
            List[int] -- A list of node_ids that are adjacent to the node with node ID node_id. Empty list if the node is invalid.
        '''
        if not self.is_valid_node(node_id):
            return []

        return [x for x in _directed_adjacency_matrix[node_id] if x is not None]

    def is_adjacent(self, first_node : int, second_node : int) -> bool:
        """Checks whether two nodes are adjacent to each other.

        Arguments:
            first_node {int} -- the first node
            second_node {int} -- the node to check adjacency to

        Returns:
            bool -- True if first_node and second_node have an edge between them. Otherwise False.
        """        
        adjacent_nodes = self.get_neighbors(first_node)

        return second_node in adjacent_nodes

    def get_nodes(self) -> List[Node]:
        '''Get a list of all Nodes on the board.

        Returns:
            List[Node] -- A list of all Nodes on the board.
        '''
        return self.__graph

    def is_valid_node(self, node_id) -> bool:
        '''Returns whether a given node ID is one that exists on the board.

        Arguments:
            node_id {int} -- ID of the node to check

        Returns:
            bool -- True if node_id is on the board, otherwise False.
        '''
        return node_id in range(0, len(self.get_nodes()))

    def get_node(self, node_id : int) -> Node or None:
        '''Gets the node with a given ID.

        Arguments:
            node_id {int} -- The ID of the node to get.

        Returns:
            Node or None -- Node with the given ID if it exists, else None
        '''
        if self.is_valid_node(node_id):
            return self.__graph[node_id]
        else:
            return None

    def is_occupied(self, node_id : int) -> bool:
        '''Check if a given node ID is occupied by some piece.

        Arguments:
            node_id {int} -- ID of the node to check

        Returns:
            bool -- True if there is a piece at the given node, else False
        '''
        return self.__graph[node_id].is_occupied()

    def get_occupied_nodes(self) -> List[Node]:
        '''Gets all occupied nodes on the board

        Returns:
            List[Node] -- A list of nodes that are currently occupied by a piece
        '''
        occupied_nodes = []
        for node in self.get_nodes():
            if node.is_occupied():
                occupied_nodes.append(node)
        return occupied_nodes

    def nodes_occupied_by_player(self, player : Player) -> List[int]:
        """Gets a list of node ids that a given player has pieces at.

        Arguments:
            player {Player} -- the given player

        Returns:
            List[int] -- A list of node ids that the player has pieces on. May be an empty list.
        """        
        if player is None:
            return []

        occupied_nodes = self.get_occupied_nodes()
        nodes_occupied_by_player = []

        for node in occupied_nodes:
            if node.piece is not None and node.piece.owner == player:
                nodes_occupied_by_player.append(node.node_id)

        return nodes_occupied_by_player

    def set_piece(self, node_id : int, owner : Player):
        '''Set a piece on the given node with the given player owner.

        The caller must ensure that the id is valid. Any piece already on the node will be replaced.

        Arguments:
            node_id {int} -- ID of the node to set the piece at\n
            owner {Player} -- The player that owns the piece
        '''
        self.__graph[node_id].piece = Piece(owner)
        self.trigger_state_event()

    def remove_piece(self, node_id : int) -> Player or None:
        '''Remove a piece from a given node on the board.

        The caller must ensure the node id is valid.

        Arguments:
            node_id {int} -- ID of the node to remove from

        Returns:
            Player or None -- The owner of the piece that was removed, or None if there was no piece at the Node
        '''
        if self.__graph[node_id].piece is None:
            return None

        # remove from cached mills, if any
        self.__remove_from_mills(self.get_node(node_id))

        owner = self.__graph[node_id].piece.owner
        self.__graph[node_id].piece = None

        self.trigger_state_event()
        return owner

    def move_piece_to(self, from_node_id : int, to_node_id : int):
        """Moves a piece from one node id to another.

        The caller must ensure the node id is valid. Any pieces already on the destination node are replaced.
        Trying to move a piece from an empty node, or trying to move to the same node has no effect.

        Arguments:
            from_node_id {int} -- the node id to move the piece from
            to_node_id {int} -- the node id to move the piece to
        """

        from_node = self.__graph[from_node_id]
        to_node = self.__graph[to_node_id]

        if from_node.piece is None or from_node_id == to_node_id:
            return

        piece_to_move = from_node.piece
        from_node.piece = None
        to_node.piece = piece_to_move


        self.__remove_from_mills(self.get_node(from_node_id))

        self.trigger_state_event()

    def is_mill_at(self, node_id : int) -> bool:
        '''Check if the given node_id is part of a mill

        Arguments:
            node_id {int} -- ID of the node to check if part of a mill

        Returns:
            bool -- True if the node is part of a mill else False
        '''
        node = self.get_node(node_id)
        if node is None:
            return False

        for mill in self.__mills:
            if node in mill:
                return True
        # No existing mills, can we generate mills?

        return self.__try_generate_mill(node_id)

    def piece_can_move_to_neighbors(self, node_id : int) -> bool:
        """Returns whether a piece on this node can move to an adjacent node.

        Arguments:
            node_id {int} -- the node ID the piece is on

        Returns:
            bool -- True if there is a piece on the node and it can move to an adjacent node, otherwise False
        """
        node = self.get_node(node_id)
        if node is None or node.piece is None:
            return False

        adjacent_nodes = map(lambda x: self.get_node(x), self.get_neighbors(node_id))

        for adjacent_node in adjacent_nodes:
            if not adjacent_node.is_occupied():
                return True
        return False

    # Tries to generate one or several mills and add them to the list of mills, given that the generated mills do not already exist.
    def __try_generate_mill(self, node_id : int) -> bool:
        start_node = self.__graph[node_id]

        # Can't generate mill starting from an empty node
        if start_node is None or start_node.piece is None:
            return False

        nodes_per_dir : List[Node] = [None] * len(list(Direction))

        for dir in Direction:
            nodes_per_dir[dir] = self.__get_consecutive_nodes(start_node, dir, [])

        vertical_nodes = nodes_per_dir[Direction.NORTH] + nodes_per_dir[Direction.SOUTH]
        horizontal_nodes = nodes_per_dir[Direction.EAST] + nodes_per_dir[Direction.WEST]
        diagonal_nodes = nodes_per_dir[Direction.SOUTH_EAST] + nodes_per_dir[Direction.SOUTH_WEST] \
        + nodes_per_dir[Direction.NORTH_EAST] + nodes_per_dir[Direction.NORTH_WEST]

        has_formed_mill = False

        if len(vertical_nodes) >= 2:
            if self.__add_mill(vertical_nodes + [start_node]):
                has_formed_mill = True
        if len(horizontal_nodes) >= 2:
            if self.__add_mill(horizontal_nodes + [start_node]):
                has_formed_mill = True
        if len(diagonal_nodes) >= 2:
            if self.__add_mill(diagonal_nodes + [start_node]):
                has_formed_mill = True

        return has_formed_mill

    def __add_mill(self, new_mill : List[Node]) -> bool:
        set_of_mills = map(lambda x: set(x), self.__mills)
        new_mill_set = set(new_mill)
        if new_mill_set not in set_of_mills:
            self.__mills.append(new_mill)
            return True
        return False

    def __remove_from_mills(self, node_to_remove : Node):
        # get the mills that this node belongs to, if any
        mills_to_remove = []
        for mill in self.__mills:
            if node_to_remove in mill:
                mills_to_remove.append(mill)

        # remove the mills
        for mill in mills_to_remove:
            self.__remove_mill(mill)

    def __remove_mill(self, mill_to_remove : List[Node]) -> bool:
        set_of_mills = list(map(lambda x: set(x), self.__mills))
        mill_set_to_remove = set(mill_to_remove)
        index_to_remove = set_of_mills.index(mill_set_to_remove)
        self.__mills.pop(index_to_remove)

    def __get_node_dir(self, node : Node, dir : Direction) -> Node or None:
        next_node_id = _directed_adjacency_matrix[node.node_id][dir]
        if next_node_id is None:
            return None
        return self.__graph[next_node_id]

    def __get_consecutive_nodes(self, current_node : Node, dir : Direction, acc : List[Node] = []):
        next_node = self.__get_node_dir(current_node, dir)
        if next_node is None or current_node.piece != next_node.piece:
            return acc
        acc.append(next_node)
        return self.__get_consecutive_nodes(next_node, dir, acc)

# Subject to interface change
class GameModel(StateObservable):
    """
    Represents the state of the game.

    Attributes:
        board {Board} -- The board associated with this game state.
    """
    board : Board
    __current_player : int = 0 # first player is always the first index
    __players : Tuple[Player, Player] # players are in order: (BLACK, WHITE)
    __turn_counter = 0

    def __init__(self):
        super().__init__()
        self.board = Board()
        self.__players = (Player(Color.BLACK), Player(Color.WHITE))
        self.board.register_listener(self.__notify_state_change)
        for player in self.__players:
            player.register_listener(self.__notify_state_change)

    def next_player(self) -> Player:
        '''Swap turn to next player.

        Returns:
            Player -- The next player to play
        '''
        self.__current_player = self.__players.index(self.get_next_player())
        return self.__players[self.__current_player]
    
    def get_next_player(self) -> Player:
        """Get the next player.

        Returns:
            Player -- the next player
        """
        return self.__players[(self.__current_player + 1) % len(self.__players)]
    
    def set_player_name(self, color : Color, new_name : str):
        """Sets the name of a player with a given color.

        Arguments:
            color {Color} -- the color of the player whose name should be set
            new_name {str} -- the new name of the player
        """        
        player = self.get_player_by_color(color)
        if player is None:
            return

        player.set_name(new_name)

    def set_ai_player(self, color : Color, ai_difficulty : AiDifficulty = AiDifficulty.EASY):
        """Enables AI for a player with a given color.

        Arguments:
            color {Color} -- the color of the player

        Keyword Arguments:
            ai_difficulty {AiDifficulty} -- the difficulty of the AI. AiDifficulty.NONE disables the AI for this player. (default: {AiDifficulty.EASY})
        """        
        player = self.get_player_by_color(color)
        if player is None: 
            return

        if ai_difficulty == AiDifficulty.NONE:
            player.disable_ai()
        
        player.enable_ai(ai_difficulty)

    def set_network_player(self, color : Color):
        player = self.get_player_by_color(color)
        if player is None: 
            return

        #if ai_difficulty == AiDifficulty.NONE:
        #    player.disable_ai()
        
        #player.enable_ai(ai_difficulty)
        player.__isnetworkplayer = True
        
    def set_turn_count(self, turn_count : int):
        '''Sets current turn number.

        Arguments:
            turn_count {int} -- Turn number to set
        '''
        self.__turn_counter = turn_count

    def get_turn_count(self) -> int:
        '''Gets the current turn number.

        Returns:
            int -- Current turn number
        '''
        return self.__turn_counter

    def get_all_players(self) -> List[Player]:
        """Gets a list of all players in the game.

        Returns:
            List[Player] -- the list of players in the game
        """        
        return list(self.__players)
    
    def get_player_by_color(self, color : Color) -> Player or None:
        """Gets the first occurence of a player based on the player's color.

        Arguments:
            color {Color} -- the color of the player

        Returns:
            Player or None -- The player with the given color, or None if no such player exists.
        """        
        for player in self.__players:
            if player.color == color:
                return player
        return None

    def get_current_player(self) -> Player:
        '''Gets the current player.

        Returns:
            Player -- Current Player
        '''
        return self.__players[self.__current_player]

    def to_ai_input(self, which_player : Player) -> Dict:
        """Converts the current state of the model to a format readable by an AI module.
        Note that there may be multiple AI players.
        Arguments:
            which_player {Player} -- the ai player for which this input is formatted

        Returns:
            Dict -- a dictionary representing the current game state. The format is defined in ai_schema.json.
        """
        data = {}
        data["version"] = 2
        data["ai_difficulty"] = str(which_player.get_ai_difficulty())
        data["state"] = {}

        data["state"]["turns_left"] = GameConfig.MAX_TURNS - self.get_turn_count()

        opponent = self.__players[(self.__players.index(which_player) + 1) % len(self.__players)] # next player, needs to be rewritten for more than 2 players
        data["state"]["they"] = {}
        data["state"]["they"]["pieces_onboard"] = self.board.nodes_occupied_by_player(opponent)
        data["state"]["they"]["pieces_offboard"] = opponent.get_pieces_to_place()

        data["state"]["we"] = {}
        data["state"]["we"]["pieces_onboard"] = self.board.nodes_occupied_by_player(which_player)
        data["state"]["we"]["pieces_offboard"] = which_player.get_pieces_to_place()
        return data
    
    def load_ai_output(self, which_player : Player, data : Dict):

        new_state = data["state"]
        new_state["we"]["pieces_onboard"]
        which_player.set_pieces_to_place(new_state["we"]["pieces_offboard"])
        self.__load_nodes(which_player, new_state["we"]["pieces_onboard"])

        opponent = self.__players[(self.__players.index(which_player) + 1) % len(self.__players)] # next player, needs to be rewritten for more than 2 players
        self.__load_nodes(opponent, new_state["they"]["pieces_onboard"])
        opponent.set_pieces_to_place(new_state["they"]["pieces_offboard"])

        which_player.set_active_pieces(len(self.board.nodes_occupied_by_player(which_player)) + which_player.get_pieces_to_place())
        opponent.set_active_pieces(len(self.board.nodes_occupied_by_player(opponent)) + opponent.get_pieces_to_place())
    
    def __load_nodes(self, player : Player, new_nodes : List[int]):
        old_nodes_set = set(self.board.nodes_occupied_by_player(player))
        new_nodes_set = set(new_nodes)
        if old_nodes_set == new_nodes_set:
            return
        
        removed_nodes = old_nodes_set - new_nodes_set
        for node_id in removed_nodes:
            owner = self.board.remove_piece(node_id)

        added_nodes =  new_nodes_set - old_nodes_set
        for node_id in added_nodes:
            self.board.set_piece(node_id, player)


    def __notify_state_change(self):
        self.trigger_state_event()


# entry point should be main.py
def main():
    pass

if __name__ == "__main__":
    main()
