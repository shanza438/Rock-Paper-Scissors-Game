"""Core rules for the Rock Paper Scissors arcade game."""

import random

CHOICES = ("rock", "paper", "scissors")
WINNING_MOVES = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}


def get_computer_choice():
    """Return a randomly selected computer move."""
    return random.choice(CHOICES)


def determine_winner(player, computer):
    """Return 'Player', 'Computer', or 'Draw'; reject invalid moves."""
    player = player.lower().strip()
    computer = computer.lower().strip()

    if player not in CHOICES or computer not in CHOICES:
        raise ValueError("Both choices must be rock, paper, or scissors.")

    if player == computer:
        return "Draw"
    return "Player" if WINNING_MOVES[player] == computer else "Computer"
