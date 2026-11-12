from collections import Counter
from core.game_logic import CHOICES, counter_move, get_computer_choice
def choose_ai_move(player_history):
    """Predict the player's most frequent move, then counter it."""
    if len(player_history)<2: return get_computer_choice()
    predicted=Counter(player_history).most_common(1)[0][0]
    # Controlled randomness prevents a perfectly deterministic opponent.
    import random
    return counter_move(predicted) if random.random()<0.70 else get_computer_choice()
