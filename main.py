
"""RPS Battle Arena - A playful Tkinter Rock Paper Scissors game."""

import copy
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from data_structures import (
    GameHistory,
    GameStack,
    RecentMovesQueue,
    ScoreBoard
)

from game_logic import CHOICES, determine_winner, get_computer_choice


# ------------------------------ THEME ------------------------------

BG = "#160D29"
PANEL = "#2B1A49"
PANEL_DARK = "#211437"
PURPLE = "#8B5CF6"
PINK = "#E879F9"
BLUE = "#60A5FA"
GOLD = "#FCD34D"
WHITE = "#FFFFFF"
MUTED = "#D8C9F4"
GREEN = "#86EFAC"
RED = "#FDA4AF"

MOVE_EMOJI = {
    "rock": "🪨",
    "paper": "📄",
    "scissors": "✂️"
}

RESULT_COLOR = {
    "Player": GREEN,
    "Computer": RED,
    "Draw": GOLD
}

RESULT_TITLE = {
    "Player": "YOU WIN!",
    "Computer": "ROBOT WINS!",
    "Draw": "IT'S A DRAW!"
}

REACTIONS = {
    "Player": [
        ("LET'S GOOOO!", "No way! You actually beat me! 🤖"),
        ("MAIN CHARACTER ENERGY!", "I need a software update... 😵"),
        ("ROBOT DOWN!", "That move was 100% human genius! ✨"),
        ("TOO EASY!", "Okay, okay... beginner's luck! 🙄"),
    ],

    "Computer": [
        ("BEEP BOOP!", "The robot brain wins again! 🤖"),
        ("GOTCHA!", "Did you just lose to a toaster? 😂"),
        ("ROBOT POWER!", "My circuits are doing a happy dance!"),
        ("NICE TRY!", "Your comeback story starts next round! 💪"),
    ],

    "Draw": [
        ("TWINS!", "We share one brain cell. 🤝"),
        ("GREAT MINDS!", "Nobody wins. The drama continues! 👀"),
        ("COPYCAT!", "Stop reading my circuits! 😆"),
    ],
}


CHALLENGE_TEMPLATES = [
    {
        "kind": "win",
        "target": 1,
        "description": "Win your next round!",
        "title": "QUICK VICTORY"
    },
    {
        "kind": "streak",
        "target": 2,
        "description": "Win 2 rounds in a row!",
        "title": "DOUBLE TROUBLE"
    },
    {
        "kind": "play",
        "target": 3,
        "description": "Play 3 rounds. Don't give up!",
        "title": "KEEP IT GOING"
    },
    {
        "kind": "move",
        "target": 1,
        "description": "Win a round using {move}!",
        "title": "SPECIAL MOVE"
    },
]


# ======================== GAME CLASS ========================

class RPSBattleArena:

    def __init__(self, root):

        self.root = root

        root.title("RPS Battle Arena | You vs. The Cheeky Robot")
        root.geometry("960x900")
        root.resizable(False, False)
        root.configure(bg=BG)

        # ---------------- DSA OBJECTS ----------------

        self.history = GameHistory()             # List
        self.undo_stack = GameStack()            # Stack
        self.recent_queue = RecentMovesQueue(5)  # Queue
        self.scoreboard = ScoreBoard()           # Dictionary

        # ---------------- GAME VARIABLES ----------------

        self.streak = 0
        self.best_streak = 0

        self.challenge = self.new_challenge()

        self.sound_enabled = True

        self.animation_jobs = []

        self.confetti_items = []

        # Initialize interface

        self.load_character_images()

        self.build_interface()

        self.update_all_displays()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_game
        )


    # ================= ASSETS / HELPERS =================

    def load_character_images(self):

        asset_dir = (
            Path(__file__).resolve().parent
            / "assets"
            / "icons"
        )

        self.player_image = None
        self.computer_image = None

        try:

            self.player_image = tk.PhotoImage(
                file=str(asset_dir / "player.png")
            ).subsample(3, 3)

            self.computer_image = tk.PhotoImage(
                file=str(asset_dir / "computer.png")
            ).subsample(3, 3)

        except tk.TclError:

            # Emoji characters are used if images are unavailable.
            self.player_image = None
            self.computer_image = None


    @staticmethod
    def card(
        parent,
        width=None,
        height=None,
        color=PANEL,
        border="#7042B8"
    ):

        frame = tk.Frame(
            parent,
            bg=color,
            highlightthickness=2,
            highlightbackground=border
        )

        if width and height:

            frame.configure(
                width=width,
                height=height
            )

            frame.pack_propagate(False)

        return frame


    def new_challenge(self):

        template = copy.deepcopy(
            random.choice(CHALLENGE_TEMPLATES)
        )

        if template["kind"] == "move":

            template["move"] = random.choice(CHOICES)

            template["description"] = (
                template["description"].format(
                    move=template["move"].upper()
                )
            )

        template["progress"] = 0

        return template


    # ================= SOUND EFFECTS =================

    def play_sound(self, kind):

        if not self.sound_enabled:
            return

        try:

            import winsound

            patterns = {

                "click": [(700, 45)],

                "win": [
                    (880, 90),
                    (1100, 120),
                    (1320, 150)
                ],

                "lose": [
                    (500, 130),
                    (360, 180)
                ],

                "draw": [
                    (650, 80),
                    (650, 80)
                ],

                "challenge": [
                    (900, 70),
                    (1200, 100)
                ],
            }

            for frequency, duration in patterns.get(
                kind,
                [(700, 60)]
            ):

                winsound.Beep(frequency, duration)

        except (ImportError, RuntimeError, tk.TclError):

            try:
                self.root.bell()

            except tk.TclError:
                pass


    # ================= CHARACTER ANIMATION =================

    def bounce_character(self, widget):

        base_y = 23

        offsets = [0, -7, -13, -7, 0]

        for index, offset in enumerate(offsets):

            job = self.root.after(
                index * 65,
                lambda y=base_y + offset: widget.place_configure(y=y)
            )

            self.animation_jobs.append(job)


    # ================= GUI INTERFACE =================

    def build_interface(self):

        # Background canvas for confetti

        self.fx_canvas = tk.Canvas(
            self.root,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        self.fx_canvas.place(
            x=0,
            y=0,
            width=960,
            height=900
        )

        self.fx_canvas.tk.call(
            "lower",
            self.fx_canvas._w
        )


        # Heading

        header = tk.Frame(
            self.root,
            bg=BG
        )

        header.pack(
            fill="x",
            pady=(17, 3)
        )

        tk.Label(
            header,
            text="RPS BATTLE ARENA",
            font=("Arial", 29, "bold"),
            bg=BG,
            fg=WHITE
        ).pack()

        tk.Label(
            header,
            text="YOU vs. THE CHEEKY ROBOT  •  Choose your move!",
            font=("Arial", 12, "bold"),
            bg=BG,
            fg=MUTED
        ).pack(pady=(3, 0))


        # ---------------- SCORE / CHARACTER PANELS ----------------

        score_row = tk.Frame(
            self.root,
            bg=BG
        )

        score_row.pack(pady=(16, 11))


        # Player card

        self.player_card = self.card(
            score_row,
            390,
            158,
            PANEL,
            PURPLE
        )

        self.player_card.pack(
            side="left",
            padx=9
        )


        # Computer card

        self.computer_card = self.card(
            score_row,
            390,
            158,
            PANEL,
            BLUE
        )

        self.computer_card.pack(
            side="left",
            padx=9
        )


        # Player character

        if self.player_image:

            self.player_portrait = tk.Label(
                self.player_card,
                image=self.player_image,
                bg=PANEL
            )

        else:

            self.player_portrait = tk.Label(
                self.player_card,
                text="🧑‍🎤",
                font=("Arial", 55),
                bg=PANEL,
                fg=WHITE
            )

        self.player_portrait.place(
            x=12,
            y=23
        )


        # Computer character

        if self.computer_image:

            self.computer_portrait = tk.Label(
                self.computer_card,
                image=self.computer_image,
                bg=PANEL
            )

        else:

            self.computer_portrait = tk.Label(
                self.computer_card,
                text="🤖",
                font=("Arial", 55),
                bg=PANEL,
                fg=WHITE
            )

        self.computer_portrait.place(
            x=12,
            y=23
        )


        # Player information

        p_info = tk.Frame(
            self.player_card,
            bg=PANEL
        )

        p_info.place(
            x=150,
            y=15,
            width=220,
            height=130
        )

        tk.Label(
            p_info,
            text="PLAYER",
            font=("Arial", 14, "bold"),
            bg=PANEL,
            fg=MUTED
        ).pack(pady=(2, 0))

        self.player_score_label = tk.Label(
            p_info,
            text="0",
            font=("Arial", 34, "bold"),
            bg=PANEL,
            fg=WHITE
        )

        self.player_score_label.pack()

        self.player_reaction = tk.Label(
            p_info,
            text="Ready to battle!",
            font=("Arial", 10, "bold"),
            bg=PANEL,
            fg="#F0ABFC",
            wraplength=205
        )

        self.player_reaction.pack(pady=(0, 3))


        # Computer information

        c_info = tk.Frame(
            self.computer_card,
            bg=PANEL
        )

        c_info.place(
            x=150,
            y=15,
            width=220,
            height=130
        )

        tk.Label(
            c_info,
            text="COMPUTER",
            font=("Arial", 14, "bold"),
            bg=PANEL,
            fg=MUTED
        ).pack(pady=(2, 0))

        self.computer_score_label = tk.Label(
            c_info,
            text="0",
            font=("Arial", 34, "bold"),
            bg=PANEL,
            fg=WHITE
        )

        self.computer_score_label.pack()

        self.computer_reaction = tk.Label(
            c_info,
            text="Beep boop. Bring it on!",
            font=("Arial", 10, "bold"),
            bg=PANEL,
            fg="#93C5FD",
            wraplength=205
        )

        self.computer_reaction.pack(pady=(0, 3))


        # ---------------- WIN STREAK ----------------

        self.streak_label = tk.Label(
            self.root,
            text="🔥  WIN STREAK: 0     •     BEST: 0",
            font=("Arial", 11, "bold"),
            bg=BG,
            fg=GOLD
        )

        self.streak_label.pack(pady=(0, 8))


        # ---------------- MOVE BUTTONS ----------------

        tk.Label(
            self.root,
            text="MAKE YOUR MOVE",
            font=("Arial", 17, "bold"),
            bg=BG,
            fg=WHITE
        ).pack(pady=(4, 8))


        moves_frame = tk.Frame(
            self.root,
            bg=BG
        )

        moves_frame.pack(pady=1)

        move_buttons = [

            ("🪨  ROCK", "rock", "#4169D8"),

            ("📄  PAPER", "paper", "#C63E9D"),

            ("✂️  SCISSORS", "scissors", "#7845CE")

        ]

        self.move_buttons = []

        for label, move, color in move_buttons:

            button = tk.Button(
                moves_frame,
                text=label,
                command=lambda m=move: self.play_round(m),
                font=("Arial", 13, "bold"),
                bg=color,
                fg=WHITE,
                activebackground="#B794F4",
                activeforeground=WHITE,
                width=17,
                height=2,
                relief="flat",
                bd=0,
                cursor="hand2"
            )

            button.pack(
                side="left",
                padx=8
            )

            self.move_buttons.append(button)


        # ---------------- CHALLENGE PANEL ----------------

        challenge_card = self.card(
            self.root,
            820,
            76,
            PANEL_DARK,
            "#A855F7"
        )

        challenge_card.pack(pady=(13, 8))

        tk.Label(
            challenge_card,
            text="🎯  MINI CHALLENGE",
            font=("Arial", 11, "bold"),
            bg=PANEL_DARK,
            fg=GOLD
        ).pack(pady=(7, 0))

        self.challenge_label = tk.Label(
            challenge_card,
            text="",
            font=("Arial", 12, "bold"),
            bg=PANEL_DARK,
            fg=WHITE
        )

        self.challenge_label.pack(pady=(2, 0))


        # ---------------- RESULT CARD ----------------

        self.result_card = self.card(
            self.root,
            820,
            104,
            PANEL,
            "#D879F9"
        )

        self.result_card.pack(pady=8)

        self.choice_label = tk.Label(
            self.result_card,
            text="YOU: —     VS     ROBOT: —",
            font=("Arial", 12, "bold"),
            bg=PANEL,
            fg=MUTED
        )

        self.choice_label.pack(pady=(11, 3))

        self.result_label = tk.Label(
            self.result_card,
            text="Let's play! The robot thinks it can win...",
            font=("Arial", 17, "bold"),
            bg=PANEL,
            fg=GOLD,
            wraplength=780
        )

        self.result_label.pack(pady=(2, 8))


        # ---------------- CONTROL BUTTONS ----------------

        controls = tk.Frame(
            self.root,
            bg=BG
        )

        controls.pack(pady=(14, 5))

        self.undo_button = self.control_button(
            controls,
            "↶  UNDO",
            self.undo_round,
            "#6540B5",
            state=tk.DISABLED
        )

        self.control_button(
            controls,
            "📖  HISTORY",
            self.show_history,
            "#6540B5"
        )

        self.control_button(
            controls,
            "⟳  RESTART",
            self.restart_game,
            "#6540B5"
        )

        self.sound_button = self.control_button(
            controls,
            "🔊 SOUND ON",
            self.toggle_sound,
            "#4D367C",
            width=14
        )

        self.control_button(
            controls,
            "EXIT",
            self.close_game,
            "#9F293F"
        )


        # Footer

        tk.Label(
            self.root,
            text="Made for fun • Powered by Python + Tkinter + DSA",
            font=("Arial", 9),
            bg=BG,
            fg="#A99AC7"
        ).pack(pady=(5, 0))


    # ---------------- CONTROL BUTTON HELPER ----------------

    def control_button(
        self,
        parent,
        text,
        command,
        color,
        state=tk.NORMAL,
        width=12
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 9, "bold"),
            bg=color,
            fg=WHITE,
            activebackground=PURPLE,
            activeforeground=WHITE,
            width=width,
            height=2,
            relief="flat",
            cursor="hand2",
            state=state
        )

        button.pack(
            side="left",
            padx=4
        )

        return button


    # ================= CHALLENGES =================

    def update_challenge(self, player_move, result):

        kind = self.challenge["kind"]

        if kind == "play":

            self.challenge["progress"] += 1

        elif kind == "win" and result == "Player":

            self.challenge["progress"] += 1

        elif kind == "streak":

            self.challenge["progress"] = self.streak

        elif (
            kind == "move"
            and result == "Player"
            and player_move == self.challenge["move"]
        ):

            self.challenge["progress"] += 1

        completed = (
            self.challenge["progress"]
            >= self.challenge["target"]
        )

        return completed


    def update_challenge_display(self):

        c = self.challenge

        self.challenge_label.config(
            text=(
                f"{c['title']}  •  "
                f"{c['description']}  "
                f"({min(c['progress'], c['target'])}/{c['target']})"
            )
        )


    # ================= GAME FUNCTION =================

    def play_round(self, player_move):

        computer_move = get_computer_choice()

        result = determine_winner(
            player_move,
            computer_move
        )

        # Save previous state for Undo

        challenge_before = copy.deepcopy(self.challenge)

        streak_before = self.streak

        # Update streak

        if result == "Player":

            self.streak += 1

            self.best_streak = max(
                self.best_streak,
                self.streak
            )

        else:

            self.streak = 0


        # Update challenge

        completed = self.update_challenge(
            player_move,
            result
        )


        # Store round in List

        round_data = self.history.add_round(
            player_move,
            computer_move,
            result,
            streak_before=streak_before,
            challenge_before=challenge_before,
            challenge_completed=completed
        )


        # Store round in Stack

        self.undo_stack.push(round_data)


        # Store round in Queue (internal only)

        self.recent_queue.enqueue(round_data)


        # Update Dictionary scores

        self.scoreboard.update(result)


        # Funny reactions

        title, robot_line = random.choice(
            REACTIONS[result]
        )


        # Display choices

        self.choice_label.config(
            text=(
                f"YOU  {MOVE_EMOJI[player_move]} "
                f"{player_move.upper()}     VS     "
                f"{MOVE_EMOJI[computer_move]} "
                f"{computer_move.upper()}  ROBOT"
            )
        )


        # Display result

        self.result_label.config(
            text=f"{RESULT_TITLE[result]}  {title}",
            fg=RESULT_COLOR[result]
        )


        self.player_reaction.config(
            text=random.choice(
                [
                    "Let's gooo!",
                    "I got this!",
                    "Human power! ✨"
                ]
                if result != "Computer"
                else [
                    "Oops...",
                    "I can recover!",
                    "Plot twist? 😅"
                ]
            )
        )

        self.computer_reaction.config(
            text=robot_line
        )


        # Character animation

        self.bounce_character(
            self.player_portrait
            if result == "Player"
            else self.computer_portrait
        )


        # Sound effects

        self.play_sound(
            "win"
            if result == "Player"
            else "lose"
            if result == "Computer"
            else "draw"
        )


        # Confetti after player victory

        if result == "Player":

            self.launch_confetti()


        # Challenge completed

        if completed:

            self.result_label.config(
                text=f"{RESULT_TITLE[result]}  •  CHALLENGE COMPLETE! 🏆",
                fg=GOLD
            )

            self.play_sound("challenge")

            self.challenge = self.new_challenge()


        self.update_all_displays()


    # ================= UNDO FUNCTION =================

    def undo_round(self):

        last_round = self.undo_stack.pop()

        if last_round is None:
            return


        # Remove last round from List

        self.history.remove_last_round()


        # Restore previous score

        self.scoreboard.undo(
            last_round["result"]
        )


        # Restore streak and challenge

        self.streak = last_round["streak_before"]

        self.challenge = copy.deepcopy(
            last_round["challenge_before"]
        )


        # Rebuild Queue

        self.recent_queue.rebuild(
            self.history.get_history()
        )


        remaining = self.history.get_history()

        if remaining:

            last = remaining[-1]

            self.choice_label.config(
                text=(
                    f"YOU  {MOVE_EMOJI[last['player']]} "
                    f"{last['player'].upper()}     VS     "
                    f"{MOVE_EMOJI[last['computer']]} "
                    f"{last['computer'].upper()}  ROBOT"
                )
            )

            self.result_label.config(
                text="LAST ROUND UNDONE  •  Try a different move! ↩",
                fg=GOLD
            )

        else:

            self.choice_label.config(
                text="YOU: —     VS     ROBOT: —"
            )

            self.result_label.config(
                text="Your comeback starts now! 🎮",
                fg=GOLD
            )

            self.player_reaction.config(
                text="Ready for a rematch!"
            )

            self.computer_reaction.config(
                text="I wasn't even trying. 🤖"
            )

        self.update_all_displays()


    # ================= DISPLAY UPDATES =================

    def update_all_displays(self):

        scores = self.scoreboard.get_scores()

        self.player_score_label.config(
            text=str(scores["Player"])
        )

        self.computer_score_label.config(
            text=str(scores["Computer"])
        )

        self.streak_label.config(
            text=(
                f"🔥  WIN STREAK: {self.streak}     "
                f"•     BEST: {self.best_streak}"
            )
        )

        # Queue remains active internally.
        # Recent moves are no longer displayed on the interface.

        self.undo_button.config(
            state=(
                tk.NORMAL
                if not self.undo_stack.is_empty()
                else tk.DISABLED
            )
        )

        self.update_challenge_display()


    # ================= CONFETTI ANIMATION =================

    def launch_confetti(self):

        colors = [
            "#F472B6",
            "#FCD34D",
            "#60A5FA",
            "#A78BFA",
            "#86EFAC"
        ]

        particles = []

        for _ in range(42):

            x = random.randint(80, 880)

            y = random.randint(100, 720)

            size = random.randint(3, 6)

            item = self.fx_canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill=random.choice(colors),
                outline=""
            )

            particles.append(
                (
                    item,
                    random.randint(-3, 3),
                    random.randint(2, 7)
                )
            )

        self.animate_confetti(
            particles,
            0
        )


    def animate_confetti(self, particles, frame):

        if frame >= 22:

            for item, _, _ in particles:

                self.fx_canvas.delete(item)

            return


        for item, dx, dy in particles:

            self.fx_canvas.move(
                item,
                dx,
                dy
            )


        self.root.after(
            35,
            lambda: self.animate_confetti(
                particles,
                frame + 1
            )
        )


    # ================= HISTORY WINDOW =================

    def show_history(self):

        window = tk.Toplevel(self.root)

        window.title("Round History")

        window.geometry("590x480")

        window.configure(bg=BG)


        tk.Label(
            window,
            text="📜  YOUR BATTLE HISTORY",
            font=("Arial", 18, "bold"),
            bg=BG,
            fg=WHITE
        ).pack(pady=15)


        wrap = tk.Frame(
            window,
            bg=BG
        )

        wrap.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 18)
        )


        scroll = tk.Scrollbar(wrap)

        scroll.pack(
            side="right",
            fill="y"
        )


        history_text = tk.Text(
            wrap,
            bg=PANEL_DARK,
            fg=MUTED,
            font=("Arial", 11),
            relief="flat",
            wrap="word",
            yscrollcommand=scroll.set,
            padx=14,
            pady=12
        )

        history_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll.config(
            command=history_text.yview
        )


        games = self.history.get_history()

        if not games:

            history_text.insert(
                "end",
                "No rounds yet. The robot is waiting for a challenger!"
            )

        else:

            for number, game in enumerate(
                games,
                start=1
            ):

                history_text.insert(
                    "end",
                    (
                        f"ROUND {number}\n"
                        f"You: {MOVE_EMOJI[game['player']]} "
                        f"{game['player'].title()}\n"
                        f"Robot: {MOVE_EMOJI[game['computer']]} "
                        f"{game['computer'].title()}\n"
                        f"Result: {game['result']}\n"
                        f"{'─' * 38}\n\n"
                    )
                )


        history_text.config(
            state="disabled"
        )


    # ================= RESTART FUNCTION =================

    def restart_game(self):

        if (
            self.history.get_history()
            and not messagebox.askyesno(
                "New Battle?",
                "Clear this game's scores and round history?"
            )
        ):

            return


        self.history.clear()

        self.undo_stack.clear()

        self.recent_queue.clear()

        self.scoreboard.reset()

        self.streak = 0

        self.best_streak = 0

        self.challenge = self.new_challenge()


        self.choice_label.config(
            text="YOU: —     VS     ROBOT: —"
        )

        self.result_label.config(
            text="Fresh battle! The robot is ready... 🤖",
            fg=GOLD
        )

        self.player_reaction.config(
            text="Let's do this!"
        )

        self.computer_reaction.config(
            text="Beep boop. Bring it on!"
        )

        self.update_all_displays()


    # ================= SOUND TOGGLE =================

    def toggle_sound(self):

        self.sound_enabled = not self.sound_enabled

        self.sound_button.config(
            text=(
                "🔊 SOUND ON"
                if self.sound_enabled
                else "🔇 SOUND OFF"
            )
        )

        if self.sound_enabled:

            self.play_sound("click")


    # ================= EXIT FUNCTION =================

    def close_game(self):

        for job in self.animation_jobs:

            try:

                self.root.after_cancel(job)

            except tk.TclError:

                pass

        self.root.destroy()


# ======================== APPLICATION ========================

def main():

    root = tk.Tk()

    RPSBattleArena(root)

    root.mainloop()


if __name__ == "__main__":

    main()
