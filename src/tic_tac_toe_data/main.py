from game_state import create_solution_tree, GameState
from typing import TextIO

# print a game state as a json string suitable for inserting into dynamo db.
def print_json(gs: GameState, outf: TextIO):

    cells = ""
    if gs.cells:
        for cell in gs.cells:
            cells = cells + f"\"{cell}\", "
        cells = cells.strip()[:-1]

    # choices is a dict of cell number -> game state
    # convert to cell number -> game state id
    choices = ""
    if gs.children:  
        for key in gs.children:
            choices = choices + f"\"{key}\":\"{gs.children[key].game_state_id}\", "
        # remove the last comma
        choices = choices.strip()[:-1]

    print((
        f"{{\"gameState\":\"{gs.game_state_id}\", "
        f"\"winCode\":\"{gs.win_code}\", "
        f"\"choices\":{{{choices}}}, "
        f"\"cells\":[{cells}]}}"
        ), file=outf)
    
    return

# print json of all descendants a given game state
def print_child_json(gs: GameState, outf: TextIO):

    for child in gs.children.values():
        print_json(child, outf)
        print_child_json(child, outf)

    return

# generate the data file, containing about a million rows.
root = create_solution_tree()
with open("game_state_data.jsonl", "w") as outf:
    print_json(root, outf)
    print_child_json(root, outf)
