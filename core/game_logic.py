import random
CHOICES=("rock","paper","scissors")
WINNING_MOVES={"rock":"scissors","paper":"rock","scissors":"paper"}
def get_computer_choice():
    return random.choice(CHOICES)
def determine_winner(player,computer):
    player=player.lower().strip(); computer=computer.lower().strip()
    if player not in CHOICES or computer not in CHOICES:
        raise ValueError("Moves must be rock, paper, or scissors.")
    if player==computer: return "Draw"
    return "Player" if WINNING_MOVES[player]==computer else "Computer"
def counter_move(move):
    return {"rock":"paper","paper":"scissors","scissors":"rock"}[move]
