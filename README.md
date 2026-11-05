# Rock, Paper, Scissors Game

A modern graphical Rock, Paper, Scissors game developed using Python and Tkinter. The player competes against the computer, which randomly selects its move. The game determines the winner and updates the scores after every round.

## Project Overview

This project is developed as part of a Data Structures and Algorithms (DSA) assignment. Its main purpose is to demonstrate the practical implementation of data structures through an interactive game.

## Technologies Used

- **Python** – Main programming language
- **Tkinter** – Graphical User Interface (GUI)
- **Random Module** – Generates the computer's random choices
- **VS Code** – Development environment

## Game Features

- Modern dark-purple graphical interface
- Three interactive choices: Rock, Paper, and Scissors
- Random computer moves
- Automatic winner detection
- Real-time player and computer score tracking
- Restart game option
- Exit option

## Game Rules

- Rock beats Scissors.
- Paper beats Rock.
- Scissors beats Paper.
- If both players choose the same option, the round is a draw.

## Data Structures

The project aims to implement the following data structures:

| Data Structure | Purpose |
|---|---|
| List | Store game history |
| Dictionary | Manage game rules and scores |
| Stack | Implement the undo last round feature |
| Queue | Maintain recent game moves |

## Project Structure

```text
rock_paper_scissor/
│
├── main.py
├── game_logic.py
├── data_structures.py
├── README.md
│
└── assets/
    └── icons/
```

## Installation and Execution

**1. Clone the repository or download the project.**

**2. Open the project folder in VS Code.**

**3. Make sure Python is installed.**

**4. Run the following command in the terminal:**

```bash
python main.py
```

No external Python libraries are currently required.

## Future Improvements

- Complete game history tracking
- Stack-based undo functionality
- Queue-based recent moves
- Game statistics and performance tracking
- Improved GUI and user experience

## Author
Shanza
**Language:** Python  
**GUI Framework:** Tkinter
