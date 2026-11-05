
class GameHistory:
    def __init__(self):
        self.history = []

    def add_round(self, player, computer, result):
        self.history.append({
            "player": player,
            "computer": computer,
            "result": result
        })

    def show_history(self):
        if not self.history:
            print("No game history yet.")
            return

        for number, game in enumerate(self.history, start=1):
            print(
                f"Round {number}: "
                f"You: {game['player']}, "
                f"Computer: {game['computer']}, "
                f"Result: {game['result']}"
            )
