
import random

CHOICES = ["rock", "paper", "scissors"]


def get_computer_choice():
    return random.choice(CHOICES)


def determine_winner(player, computer):
    if player == computer:
        return "Draw"

    winning_moves = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper"
    }

    if winning_moves[player] == computer:
        return "Player"

    return "Computer"
