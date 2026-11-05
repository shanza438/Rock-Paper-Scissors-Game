
import tkinter as tk
from game_logic import get_computer_choice, determine_winner

# Main window
root = tk.Tk()
root.title("Rock Paper Scissors")
root.geometry("800x650")
root.resizable(False, False)

# Colors
BG = "#211C35"
CARD = "#38304F"
PURPLE = "#8B5CF6"
WHITE = "#FFFFFF"
LIGHT = "#C9BCEB"

root.configure(bg=BG)

# Scores
player_score = 0
computer_score = 0

# Heading
tk.Label(
    root,
    text="ROCK PAPER SCISSORS",
    font=("Arial", 26, "bold"),
    bg=BG,
    fg=WHITE
).pack(pady=(25, 5))

tk.Label(
    root,
    text="Choose your move and challenge the computer!",
    font=("Arial", 12),
    bg=BG,
    fg=LIGHT
).pack(pady=5)

# Score cards
score_frame = tk.Frame(root, bg=BG)
score_frame.pack(pady=25)

player_card = tk.Frame(score_frame, bg=CARD, width=220, height=105)
player_card.pack(side="left", padx=15)
player_card.pack_propagate(False)

computer_card = tk.Frame(score_frame, bg=CARD, width=220, height=105)
computer_card.pack(side="left", padx=15)
computer_card.pack_propagate(False)

tk.Label(
    player_card, text="PLAYER",
    font=("Arial", 12, "bold"),
    bg=CARD, fg=LIGHT
).pack(pady=8)

player_score_label = tk.Label(
    player_card, text="0",
    font=("Arial", 26, "bold"),
    bg=CARD, fg=WHITE
)
player_score_label.pack()

tk.Label(
    computer_card, text="COMPUTER",
    font=("Arial", 12, "bold"),
    bg=CARD, fg=LIGHT
).pack(pady=8)

computer_score_label = tk.Label(
    computer_card, text="0",
    font=("Arial", 26, "bold"),
    bg=CARD, fg=WHITE
)
computer_score_label.pack()

# Choices heading
tk.Label(
    root,
    text="MAKE YOUR CHOICE",
    font=("Arial", 18, "bold"),
    bg=BG,
    fg=WHITE
).pack(pady=15)

# Result labels
choice_label = tk.Label(
    root,
    text="You: -       Computer: -",
    font=("Arial", 14),
    bg=BG,
    fg=LIGHT
)
choice_label.pack(pady=10)

result_label = tk.Label(
    root,
    text="Let's Play!",
    font=("Arial", 22, "bold"),
    bg=BG,
    fg=WHITE
)
result_label.pack(pady=15)

# Game function
def play_game(player_choice):
    global player_score, computer_score

    computer_choice = get_computer_choice()

    result = determine_winner(player_choice, computer_choice)

    choice_label.config(
        text=f"You: {player_choice.title()}   |   "
             f"Computer: {computer_choice.title()}"
    )

    if result == "Player":
        player_score += 1
        result_label.config(text="YOU WIN!", fg="#4ADE80")

    elif result == "Computer":
        computer_score += 1
        result_label.config(text="COMPUTER WINS!", fg="#F87171")

    else:
        result_label.config(text="IT'S A DRAW!", fg="#FACC15")

    player_score_label.config(text=str(player_score))
    computer_score_label.config(text=str(computer_score))


# Choice buttons
button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=20)

choices = [
    ("✊ ROCK", "rock"),
    ("✋ PAPER", "paper"),
    ("✌ SCISSORS", "scissors")
]

for text, choice in choices:
    tk.Button(
        button_frame,
        text=text,
        font=("Arial", 13, "bold"),
        bg=PURPLE,
        fg=WHITE,
        activebackground="#A78BFA",
        activeforeground=WHITE,
        width=14,
        height=2,
        relief="flat",
        cursor="hand2",
        command=lambda c=choice: play_game(c)
    ).pack(side="left", padx=8)


# Restart function
def restart_game():
    global player_score, computer_score

    player_score = 0
    computer_score = 0

    player_score_label.config(text="0")
    computer_score_label.config(text="0")

    choice_label.config(text="You: -       Computer: -")
    result_label.config(text="Let's Play!", fg=WHITE)


# Restart and Exit buttons
bottom_frame = tk.Frame(root, bg=BG)
bottom_frame.pack(pady=20)

tk.Button(
    bottom_frame,
    text="RESTART",
    command=restart_game,
    font=("Arial", 11, "bold"),
    bg=CARD,
    fg=WHITE,
    width=15,
    cursor="hand2",
    relief="flat"
).pack(side="left", padx=10)

tk.Button(
    bottom_frame,
    text="EXIT",
    command=root.destroy,
    font=("Arial", 11, "bold"),
    bg="#7F1D1D",
    fg=WHITE,
    width=15,
    cursor="hand2",
    relief="flat"
).pack(side="left", padx=10)


root.mainloop()
