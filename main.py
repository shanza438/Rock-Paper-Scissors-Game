
import tkinter as tk
from tkinter import messagebox, simpledialog
import random

from core.game_logic import CHOICES, determine_winner
from data_structures.data_structures import (
    GameHistory,
    GameStack,
    RecentMovesQueue,
    ScoreBoard
)
from database.database import Database


# -------------------- THEME --------------------

BG = "#17132B"
PANEL = "#29213F"
PANEL2 = "#342A50"
PURPLE = "#8B6BE8"
WHITE = "#FFFFFF"
MUTED = "#B8AFCB"
GREEN = "#86EFAC"
RED = "#FDA4AF"
GOLD = "#F0C76C"

LEVELS = [
    {
        "name": "Beginner",
        "rounds": 5,
        "mode": "classic",
        "description": "Play classic Rock Paper Scissors."
    },
    {
        "name": "Speed Round",
        "rounds": 5,
        "mode": "speed",
        "description": "Make each move before the timer ends."
    },
    {
        "name": "Prediction",
        "rounds": 7,
        "mode": "prediction",
        "description": "Predict the robot's next move."
    },
    {
        "name": "Survival",
        "rounds": 0,
        "mode": "survival",
        "description": "You have three lives. Survive!"
    },
    {
        "name": "Final Boss",
        "rounds": 7,
        "mode": "boss",
        "description": "Face an adaptive AI opponent."
    }
]

EMOJI = {
    "rock": "✊",
    "paper": "✋",
    "scissors": "✌️"
}


# -------------------- MAIN APPLICATION --------------------

class RPSApp:

    def __init__(self, root):
        self.root = root
        self.root.title("RPS Evolution - Think Before You Throw")
        self.root.geometry("900x760")
        self.root.minsize(820, 680)
        self.root.configure(bg=BG)

        self.db = Database()
        self.user = None
        self.level = 0

        # Data structures
        self.history = GameHistory()
        self.undo_stack = GameStack()
        self.queue = RecentMovesQueue(5)
        self.board = ScoreBoard()

        # Match state
        self.match_rounds = []
        self.round_no = 0
        self.lives = 3
        self.undo_used = False
        self.match_finished = False

        # Timer
        self.timer_job = None
        self.time_left = 0

        self.show_login()

    # -------------------- UI HELPERS --------------------

    def clear(self):
        if self.timer_job:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass

            self.timer_job = None

        # Remove previous screen's mouse-wheel binding
        self.root.unbind_all("<MouseWheel>")

        for widget in self.root.winfo_children():
            widget.destroy()

    def title(self, parent, text, size=22):
        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold"),
            bg=parent["bg"],
            fg=WHITE
        ).pack(pady=8)

    def button(self, parent, text, cmd, color=PURPLE):
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=color,
            fg=WHITE,
            activebackground="#A78BFA",
            activeforeground=WHITE,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=10
        )

    def label(self, parent, text, size=11, color=MUTED, bold=False):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            bg=parent["bg"],
            fg=color
        )

    def card(self, parent):
        return tk.Frame(
            parent,
            bg=PANEL,
            padx=18,
            pady=14,
            highlightthickness=1,
            highlightbackground="#51416F"
        )

    def header(self, subtitle="THINK BEFORE YOU THROW"):
        self.label(
            self.root,
            "RPS Game",
            24,
            "#D2BEFF",
            True
        ).pack(pady=(16, 0))

        self.label(
            self.root,
            subtitle,
            9,
            MUTED,
            True
        ).pack(pady=(0, 12))

    # -------------------- SCROLLABLE FRAME --------------------

    def create_scrollable_frame(self):
        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        canvas = tk.Canvas(
            container,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        content = tk.Frame(canvas, bg=BG)

        content.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse-wheel scrolling on Windows
        def scroll_with_mouse(event):
            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        self.root.bind_all(
            "<MouseWheel>",
            scroll_with_mouse
        )

        return content

    # -------------------- LOGIN / REGISTER --------------------

    def show_login(self):
        self.clear()
        self.header()

        box = self.card(self.root)
        box.pack(pady=35, ipadx=30, ipady=20)

        self.title(box, "Welcome, Player!", 21)

        tabs = tk.Frame(box, bg=PANEL)
        tabs.pack(pady=8)

        self.login_form(tabs)

    def login_form(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(
            parent,
            text="Username",
            bg=PANEL,
            fg=WHITE
        ).pack(anchor="w")

        username = tk.Entry(
            parent,
            font=("Segoe UI", 12),
            width=30
        )
        username.pack(pady=(3, 12), ipady=5)

        tk.Label(
            parent,
            text="Password",
            bg=PANEL,
            fg=WHITE
        ).pack(anchor="w")

        password = tk.Entry(
            parent,
            font=("Segoe UI", 12),
            width=30,
            show="•"
        )
        password.pack(pady=(3, 15), ipady=5)

        def login():
            user = self.db.login(
                username.get().strip(),
                password.get()
            )

            if user:
                self.user = user
                self.show_dashboard()
            else:
                messagebox.showerror(
                    "Login failed",
                    "Incorrect username or password."
                )

        def register():
            if self.db.register(
                username.get().strip(),
                password.get()
            ):
                messagebox.showinfo(
                    "Account created",
                    "Your account is ready. Please log in."
                )
            else:
                messagebox.showerror(
                    "Registration failed",
                    "Choose a username (3+ characters) "
                    "and password (6+ characters)."
                )

        row = tk.Frame(parent, bg=PANEL)
        row.pack()

        self.button(row, "LOGIN", login).pack(
            side="left",
            padx=5
        )

        self.button(
            row,
            "REGISTER",
            register,
            color="#625080"
        ).pack(side="left", padx=5)

        self.label(
            parent,
            "Register using the same form, then log in.",
            9
        ).pack(pady=12)

    # -------------------- DASHBOARD --------------------

    def show_dashboard(self):
        self.clear()
        self.header("PLAYER DASHBOARD")

        content = self.create_scrollable_frame()

        top = tk.Frame(content, bg=BG)
        top.pack(fill="x", padx=30, pady=10)

        self.label(
            top,
            f"Welcome back, {self.user}",
            18,
            WHITE,
            True
        ).pack(side="left")

        self.button(
            top,
            "LOGOUT",
            self.logout,
            "#625080"
        ).pack(side="right")

        stats = self.db.stats(self.user)

        box = self.card(content)
        box.pack(fill="x", padx=30, pady=15)

        self.label(
            box,
            f"TOTAL XP: {stats['xp']}     "
            f"WINS: {stats['wins']}     "
            f"MATCHES: {stats['matches']}",
            13,
            "#D2BEFF",
            True
        ).pack()

        self.title(content, "SELECT YOUR LEVEL", 18)

        grid = tk.Frame(content, bg=BG)
        grid.pack(padx=25, pady=5)

        unlocked = max(1, stats["highest_level"] + 1)

        for i, lvl in enumerate(LEVELS):
            unlocked_now = i < unlocked

            c = self.card(grid)
            c.grid(
                row=i // 2,
                column=i % 2,
                padx=9,
                pady=8,
                sticky="nsew"
            )

            self.label(
                c,
                f"LEVEL {i + 1}",
                9,
                "#D2BEFF",
                True
            ).pack()

            self.label(
                c,
                lvl["name"],
                15,
                WHITE,
                True
            ).pack()

            self.label(
                c,
                lvl["description"],
                9
            ).pack(pady=3)

            self.label(
                c,
                "UNLOCKED" if unlocked_now else "🔒 LOCKED",
                9,
                GREEN if unlocked_now else RED,
                True
            ).pack()

            if unlocked_now:
                self.button(
                    c,
                    "PLAY",
                    lambda n=i: self.start_level(n)
                ).pack(pady=5)

        row = tk.Frame(content, bg=BG)
        row.pack(pady=15)

        self.button(
            row,
            "PROFILE & STATISTICS",
            self.show_profile,
            "#625080"
        ).pack(side="left", padx=6)

        self.button(
            row,
            "INSTRUCTIONS",
            self.instructions,
            "#625080"
        ).pack(side="left", padx=6)

    def instructions(self):
        messagebox.showinfo(
            "How to play",
            "Rock beats Scissors.\n"
            "Scissors beats Paper.\n"
            "Paper beats Rock.\n\n"
            "Complete levels in order to unlock the next one.\n"
            "Undo can be used once per match."
        )

    def logout(self):
        self.user = None
        self.show_login()

    # -------------------- START LEVEL --------------------

    def start_level(self, n):
        self.level = n

        self.history.clear()
        self.undo_stack.clear()
        self.queue.clear()
        self.board.reset()

        self.match_rounds = []
        self.round_no = 0
        self.lives = 3
        self.undo_used = False
        self.match_finished = False

        self.show_game()

    # -------------------- GAME SCREEN --------------------

    def show_game(self):
        self.clear()

        lvl = LEVELS[self.level]

        self.header(
            f"LEVEL {self.level + 1} • {lvl['name'].upper()}"
        )

        self.game_info = tk.Frame(self.root, bg=BG)
        self.game_info.pack()

        self.status = self.label(
            self.game_info,
            "",
            12,
            "#D2BEFF",
            True
        )
        self.status.pack()

        self.score = self.label(
            self.root,
            "YOU 0 — 0 ROBOT",
            17,
            WHITE,
            True
        )
        self.score.pack(pady=8)

        arena = tk.Frame(self.root, bg=BG)
        arena.pack(pady=12)

        for name, emoji in [
            ("YOU", "🧑‍🎤"),
            ("ROBOT", "🤖")
        ]:
            c = self.card(arena)
            c.pack(side="left", padx=14)

            self.label(
                c,
                emoji,
                42,
                WHITE
            ).pack()

            self.label(
                c,
                name,
                11,
                "#D2BEFF",
                True
            ).pack()

        self.prompt = self.label(
            self.root,
            lvl["description"],
            12,
            WHITE,
            True
        )
        self.prompt.pack(pady=12)

        moves = tk.Frame(self.root, bg=BG)
        moves.pack(pady=10)

        self.move_buttons = []

        for move in CHOICES:
            btn = self.button(
                moves,
                f"{EMOJI[move]}  {move.upper()}",
                lambda m=move: self.play(m)
            )
            btn.pack(side="left", padx=7)
            self.move_buttons.append(btn)

        self.feedback = self.label(
            self.root,
            "Choose your move!",
            15,
            GOLD,
            True
        )
        self.feedback.pack(pady=12)

        actions = tk.Frame(self.root, bg=BG)
        actions.pack(pady=10)

        self.undo_btn = self.button(
            actions,
            "UNDO (1 PER MATCH)",
            self.undo,
            "#625080"
        )
        self.undo_btn.pack(side="left", padx=6)

        self.button(
            actions,
            "QUIT TO MENU",
            self.show_dashboard,
            "#625080"
        ).pack(side="left", padx=6)

        self.refresh_game()

        if lvl["mode"] == "speed":
            self.start_timer()

    def refresh_game(self):
        lvl = LEVELS[self.level]

        total = (
            "∞"
            if lvl["mode"] == "survival"
            else str(lvl["rounds"])
        )

        lives_text = (
            "❤️ " * self.lives
            if lvl["mode"] == "survival"
            else "—"
        )

        self.status.config(
            text=f"ROUND {self.round_no + 1} / {total} "
                 f"• LIVES: {lives_text}"
        )

        scores = self.board.get_scores()

        self.score.config(
            text=f"YOU {scores['Player']} — "
                 f"{scores['Computer']} ROBOT"
        )

        if self.undo_used:
            self.undo_btn.config(state="disabled")

    # -------------------- SPEED TIMER --------------------

    def start_timer(self):
        self.time_left = 10
        self.timer_tick()

    def timer_tick(self):
        if not self.root.winfo_exists():
            return

        if self.match_finished:
            return

        self.prompt.config(
            text=f"⏱ Choose within {self.time_left} seconds!"
        )

        if self.time_left <= 0:
            self.timer_job = None

            self.feedback.config(
                text="Time's up! No point awarded.",
                fg=RED
            )

            self.finish_round_timeout()
            return

        self.time_left -= 1

        self.timer_job = self.root.after(
            1000,
            self.timer_tick
        )

    def finish_round_timeout(self):
        if self.match_finished:
            return

        self.round_no += 1

        if self.round_no >= LEVELS[self.level]["rounds"]:
            self.finish_match()
        else:
            self.refresh_game()
            self.start_timer()

    # -------------------- PLAY ROUND --------------------

    def play(self, player):
        if self.match_finished:
            return

        if self.timer_job:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass

            self.timer_job = None

        mode = LEVELS[self.level]["mode"]

        previous = [
            r["player"]
            for r in self.history.get_history()
        ]

        # AI chooses before processing the current player move.
        if mode == "boss" and previous:
            from ai.opponent import choose_ai_move
            computer = choose_ai_move(previous)
        else:
            computer = random.choice(CHOICES)

        result = determine_winner(player, computer)

        prediction = None

        if mode == "prediction":
            prediction = simpledialog.askstring(
                "Prediction",
                "Predict the robot's move: rock, paper, or scissors"
            )

            if prediction is None:
                return

            prediction = prediction.strip().lower()

            if prediction not in CHOICES:
                messagebox.showwarning(
                    "Invalid prediction",
                    "Enter rock, paper, or scissors."
                )

                return

        snapshot = {
            "player": player,
            "computer": computer,
            "result": result,
            "round": self.round_no + 1,
            "scores": self.board.get_scores().copy(),
            "lives": self.lives,
            "prediction": prediction
        }

        self.undo_stack.push(snapshot)

        self.history.add_round(
            player,
            computer,
            result,
            round=self.round_no + 1,
            prediction=prediction
        )

        self.queue.enqueue({
            "player": player,
            "computer": computer
        })

        self.board.update(result)

        if result == "Computer" and mode == "survival":
            self.lives -= 1

        self.round_no += 1

        msg = (
            f"You: {player.upper()} | "
            f"Robot: {computer.upper()} | "
            f"{result.upper()}!"
        )

        if mode == "prediction":
            if prediction == computer:
                msg += " Correct prediction!"
            else:
                msg += (
                    f" Prediction missed "
                    f"(robot chose {computer})."
                )

        self.feedback.config(
            text=msg,
            fg=(
                GREEN if result == "Player"
                else RED if result == "Computer"
                else GOLD
            )
        )

        self.refresh_game()

        if mode == "survival" and self.lives <= 0:
            self.finish_match()

        elif (
            mode != "survival"
            and self.round_no >= LEVELS[self.level]["rounds"]
        ):
            self.finish_match()

        elif mode == "speed":
            self.start_timer()

    # -------------------- UNDO --------------------

    def undo(self):
        if self.undo_used or self.match_finished:
            return

        data = self.undo_stack.pop()

        if not data:
            return

        self.undo_used = True

        self.history.remove_last_round()
        self.queue.rebuild(self.history.get_history())

        self.board.scores = data["scores"].copy()

        self.lives = data["lives"]
        self.round_no -= 1

        self.feedback.config(
            text="Previous round undone.",
            fg=GOLD
        )

        self.refresh_game()

        if LEVELS[self.level]["mode"] == "speed":
            self.start_timer()

    # -------------------- FINISH MATCH --------------------

    def finish_match(self):
        if self.match_finished:
            return

        self.match_finished = True

        if self.timer_job:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass

            self.timer_job = None

        for btn in getattr(self, "move_buttons", []):
            btn.config(state="disabled")

        scores = self.board.get_scores()

        outcome = (
            "Victory"
            if scores["Player"] > scores["Computer"]
            else "Defeat"
            if scores["Player"] < scores["Computer"]
            else "Draw"
        )

        won = outcome == "Victory"

        xp = (
            100 if won
            else 30 if outcome == "Draw"
            else 10
        )

        if won:
            self.db.unlock_level(
                self.user,
                self.level
            )

        self.db.save_match(
            self.user,
            self.level + 1,
            outcome,
            scores["Player"],
            scores["Computer"],
            xp
        )

        self.show_results(outcome, scores, xp)

    # -------------------- RESULTS SCREEN --------------------

    def show_results(self, outcome, scores, xp):
        self.clear()

        self.header(
            f"LEVEL {self.level + 1} RESULTS"
        )

        heading = (
            "🏆 VICTORY!"
            if outcome == "Victory"
            else "GAME OVER"
            if outcome == "Defeat"
            else "IT'S A DRAW!"
        )

        heading_color = (
            GREEN if outcome == "Victory"
            else RED if outcome == "Defeat"
            else GOLD
        )

        tk.Label(
            self.root,
            text=heading,
            font=("Segoe UI", 28, "bold"),
            bg=BG,
            fg=heading_color
        ).pack(pady=15)

        box = self.card(self.root)
        box.pack(pady=15, ipadx=45)

        self.label(
            box,
            "FULL MATCH SUMMARY",
            14,
            "#D2BEFF",
            True
        ).pack(pady=6)

        details = [
            f"Outcome: {outcome}",
            f"Your score: {scores['Player']}",
            f"Robot score: {scores['Computer']}",
            f"Rounds played: {self.round_no}",
            f"XP earned: +{xp}"
        ]

        for line in details:
            self.label(
                box,
                line,
                12,
                WHITE
            ).pack(pady=4)

        navigation = tk.Frame(self.root, bg=BG)
        navigation.pack(pady=15)

        if outcome == "Victory" and self.level < 4:
            self.button(
                navigation,
                "NEXT LEVEL",
                lambda: self.start_level(self.level + 1),
                GREEN
            ).pack(pady=6, fill="x")

        self.button(
            navigation,
            "RETRY LEVEL",
            lambda: self.start_level(self.level)
        ).pack(pady=6, fill="x")

        self.button(
            navigation,
            "BACK TO HOME",
            self.show_dashboard,
            "#625080"
        ).pack(pady=6, fill="x")

    # -------------------- PLAYER PROFILE --------------------

    def show_profile(self):
        self.clear()
        self.header("PLAYER PROFILE & STATISTICS")

        stats = self.db.stats(self.user)

        box = self.card(self.root)
        box.pack(fill="x", padx=35, pady=10)

        self.title(box, self.user, 18)

        details = [
            f"Total matches: {stats['matches']}",
            f"Wins: {stats['wins']}   "
            f"Losses: {stats['losses']}   "
            f"Draws: {stats['draws']}",
            f"Win rate: {stats['win_rate']:.1f}%",
            f"Best win streak: {stats['best_streak']}",
            f"Highest unlocked level: "
            f"{min(stats['highest_level'] + 1, 5)}",
            f"Total XP: {stats['xp']}"
        ]

        for line in details:
            self.label(
                box,
                line,
                12,
                WHITE
            ).pack(pady=3)

        self.title(
            self.root,
            "PREVIOUS MATCH HISTORY",
            15
        )

        history = self.db.matches(self.user)

        listbox = tk.Listbox(
            self.root,
            width=85,
            height=9,
            bg=PANEL,
            fg=WHITE,
            selectbackground=PURPLE,
            font=("Consolas", 10),
            bd=0
        )

        listbox.pack(padx=25, pady=5)

        if not history:
            listbox.insert(
                "end",
                "No matches played yet."
            )

        for match in history:
            listbox.insert(
                "end",
                f"Level {match[0]} | "
                f"{match[1]:7} | "
                f"You {match[2]} - {match[3]} Robot | "
                f"+{match[4]} XP | {match[5]}"
            )

        row = tk.Frame(self.root, bg=BG)
        row.pack(pady=10)

        self.button(
            row,
            "CHANGE USERNAME",
            self.change_username,
            "#625080"
        ).pack(side="left", padx=5)

        self.button(
            row,
            "CHANGE PASSWORD",
            self.change_password,
            "#625080"
        ).pack(side="left", padx=5)

        self.button(
            row,
            "HOME",
            self.show_dashboard
        ).pack(side="left", padx=5)

    # -------------------- ACCOUNT SETTINGS --------------------

    def change_username(self):
        new = simpledialog.askstring(
            "Change username",
            "Enter new username:"
        )

        if new and self.db.change_username(
            self.user,
            new.strip()
        ):
            self.user = new.strip()

            messagebox.showinfo(
                "Updated",
                "Username changed."
            )

            self.show_profile()

        elif new:
            messagebox.showerror(
                "Error",
                "Username unavailable or invalid."
            )

    def change_password(self):
        old = simpledialog.askstring(
            "Current password",
            "Enter current password:",
            show="•"
        )

        if not old:
            return

        new = simpledialog.askstring(
            "New password",
            "Enter new password:",
            show="•"
        )

        if not new:
            return

        if self.db.change_password(
            self.user,
            old,
            new
        ):
            messagebox.showinfo(
                "Updated",
                "Password changed."
            )
        else:
            messagebox.showerror(
                "Error",
                "Password change failed. Check your "
                "current password and new password length."
            )


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = RPSApp(root)
    root.mainloop()
