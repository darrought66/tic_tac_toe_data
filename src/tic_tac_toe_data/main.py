from game_state import create_solution_tree, GameState
from typing import TextIO

# print a game state as a JSon string suitable for inserting into dynamo db.
def print_json(gs: GameState, outf: TextIO):

    choices = ""
    if gs.children:  
        for key in gs.children:
            choices = choices + f"{key}:{gs.children[key]}, "
        choices = choices.strip()[:-1]

    print(f"{{gameState={gs.game_state_id}, winCode='{gs.win_code}', choices={{{choices}}}}}", file=outf)
    
    return

# print json of all descendants
def print_child_json(gs: GameState, outf: TextIO):

    for child in gs.children.values():
        print_json(child, outf)
        print_child_json(child, outf)

    return

# print out all insert statements for dynamodb
root = create_solution_tree()
with open("game_state_json.txt", "w") as outf:
    print_json(root, outf)
    print_child_json(root, outf)
