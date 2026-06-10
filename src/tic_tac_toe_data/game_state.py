from __future__ import annotations  # Must be the very first line of the file
import constants
import math
#from win_code import assign_win_codes

# a game state is a single node in the game tree. 
class GameState:

    # the game state immediately prior to this state.
    # the difference between a parent and a childs cells should be one cell and that is the move
    # that created the child. 
    parent: GameState | None = None

    # a unique integer identifying this game state.
    # for any game state A, its right sister B and an arbitrary game state C ...
    # A.game_state_id < C.game_State_id < B.game_state_id iff C is a grandchild of A.
    # the final game state will be 9!.
    game_state_id: int = 0

    # from each game state either X or O will be choosing the next move. this is the "acting"
    # player. the opposite player made the move that created this game state.
    acting_player: str = constants.X_PLAYER

    # there are three terminal states: O won, X won and Tie. 
    win_code: str = constants.IN_PROGRESS

    # this is the play surface of this state with indices numbered like this:
    #   0|1|2
    #   3|4|5
    #   6|7|8
    cells: list[str] = []

    # the states created by a single move from this state.
    children: dict[int, GameState] = {}

    def is_root(self) -> bool:
        return self.parent is None
    
    def is_leaf(self) -> bool:
        return not self.children
    
    # returns the number of moves taken to get to this game state.
    def count_moves(self) -> int:
        count = 0
        for i in range(9):
            if self.cells[i] != constants.OPEN_CELL:
                count += 1
        return count

# generates the game tree of tic tac toe.
def create_solution_tree() -> GameState:

    # create the root node
    root: GameState = GameState()
    root.game_state_id = 0
    root.acting_player = constants.X_PLAYER # X is first player
    root.win_code = constants.IN_PROGRESS
    for i in range(9):
        root.cells.append(constants.OPEN_CELL)

    # create the remaining nodes in the game tree.
    # do a sanity check that there are 9! + 1 nodes.
    actual: int = create_children(root)
    correct: int =  986410 # 1 + sum (n = 0 to 8) (9!/n!)
    if actual != correct:
        msg = f"incorrect number of children. correct {correct}, actual: {actual}"
        raise RuntimeError(msg)
    
    # assigning win codes is easier when the game tree has been comoleted.
    assign_win_codes(root)

    return root

# recursively constructs the tree.
# returns the next available game state id.
def create_children(parent: GameState) -> int:

    child_id: int = parent.game_state_id + 1

    # iterate through each cell
    for cell_number in range(9):
        # ignore any cell not open
        if parent.cells[cell_number] == constants.OPEN_CELL:
            # claim the cell for the acting player
            child: GameState = GameState()
            child.parent = parent
            parent.children[cell_number] = child
            child.children = {}
            child.game_state_id = child_id
            print(f"{parent.game_state_id} takes {child.game_state_id} as cell number {cell_number}")
            child.acting_player = opposite_player(parent.acting_player)
            # win codes are assigned after the game tree has been constructed.
            child.win_code = constants.IN_PROGRESS
            # copy parents cells and then modify the move creating this node.
            child.cells = list(parent.cells)
            child.cells[cell_number] = parent.acting_player
            child_id: int = create_children(child)

    return child_id

# X is opposite of O and vice versa.
def opposite_player(player: str) -> str:

    if player == constants.X_PLAYER:
        return constants.O_PLAYER
    
    if player == constants.O_PLAYER:
        return constants.X_PLAYER
    
    raise ValueError


# assigns terminal win codes and prunes tree.
# every branch should end with a terminal state (win or tie).
# a terminal state can only occur in a leaf.
def assign_win_codes(root: GameState):

    assign_win_codes0(root)
    sanity_check(root)

    return


# checks that all branches end with a terminal state and vice versa.
def sanity_check(gs: GameState):

    if gs.win_code == constants.IN_PROGRESS:
        if not gs.children:
            RuntimeError("a non terminal node without children")
        for child in gs.children.values():
            sanity_check(child)

    else:
        if gs.children:
            RuntimeError("a terminal node with children")

    return


def assign_win_codes0(parent: GameState):

    # a win is three moves from the same player in a row, column or diagonal. therefore
    # there would have to be at least five moves before a win could occur.
    if parent.count_moves() > 4:
        # this looks for wins only, not ties
        parent.win_code = eval_for_win(parent)
        # a win is a terminal state.
        if parent.win_code != constants.IN_PROGRESS:
            parent.children.clear()

    # assign wins/ties in all descendants
    for child in parent.children.values():
        assign_win_codes0(child)

    # recursive calls have been completed so this is processing leaf to root.

    # there are no further moves from a leaf so if it is not a win then it is a tie.
    # this guarantees that all leaves have a terminal state (win or tie).
    if parent.is_leaf() and parent.win_code == constants.IN_PROGRESS:
        parent.win_code = constants.TIED

    # any node where all the children are ties is a tie.
    if not parent.is_leaf():
        all_children_are_ties = True
        for child in parent.children.values():
            if child.win_code != constants.TIED:
                all_children_are_ties = False
                break

        if all_children_are_ties:
            parent.win_code = constants.TIED
            # a tie is a terminal state
            parent.children.clear()

    return


# evaluate all rows, columns and diagonals to see if any contain a winning pattern.
def eval_for_win(gs: GameState) -> str:

    win_code = eval_backward_diagonal(gs)
    if win_code != constants.IN_PROGRESS:
        return win_code

    win_code = eval_forward_diagonal(gs)
    if win_code != constants.IN_PROGRESS:
        return win_code

    for row in range(3):
        win_code = eval_row(gs, row)
        if win_code != constants.IN_PROGRESS:
            return win_code

        win_code = eval_column(gs, row)
        if win_code != constants.IN_PROGRESS:
            return win_code

    return constants.IN_PROGRESS


# evaluate a diagonal to see if it contains a winning pattern
def eval_forward_diagonal(gs: GameState) -> str:

    #       0|?|?
    #       ?|4|?
    #       ?|?|8

    if gs.cells[0] == gs.cells[4] and gs.cells[4] == gs.cells[8]:
        if gs.cells[0] == constants.X_PLAYER:
            return constants.X_PLAYER
        if gs.cells[0] == constants.O_PLAYER:
            return constants.O_PLAYER

    return constants.IN_PROGRESS


# evaluate a diagonal to see if it contains a winning pattern
def eval_backward_diagonal(gs: GameState) -> str:

    #       ?|?|2
    #       ?|4|?
    #       6|?|?

    if gs.cells[2] == gs.cells[4] and gs.cells[4] == gs.cells[6]:
        if gs.cells[2] == constants.X_PLAYER:
            return constants.X_PLAYER
        if gs.cells[2] == constants.O_PLAYER:
            return constants.O_PLAYER

    return constants.IN_PROGRESS


# evaluate a column to see if it contains a winning pattern
def eval_column(gs: GameState, column: int) -> str:

    if (
        gs.cells[0 + column] == gs.cells[3 + column]
        and gs.cells[3 + column] == gs.cells[6 + column]
    ):
        if gs.cells[0 + column] == constants.X_PLAYER:
            return constants.X_PLAYER
        if gs.cells[0 + column] == constants.O_PLAYER:
            return constants.O_PLAYER

    return constants.IN_PROGRESS


# evaluate a row to see if it contains a winning pattern
def eval_row(gs: GameState, row: int) -> str:

    p: int = 3 * row
    if gs.cells[0 + p] == gs.cells[1 + p] and gs.cells[1 + p] == gs.cells[2 + p]:
        if gs.cells[0 + p] == constants.X_PLAYER:
            return constants.X_PLAYER
        if gs.cells[0 + p] == constants.O_PLAYER:
            return constants.O_PLAYER

    return constants.IN_PROGRESS
