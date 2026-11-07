"""Data structures used by RPS Battle Arena.

List: complete round history
Dictionary: score board
Stack: undo the latest round (LIFO)
Queue: retain the five most recent rounds (FIFO)
"""

from collections import deque


class GameHistory:
    """List-based storage for every completed round in this session."""

    def __init__(self):
        self.history = []

    def add_round(self, player, computer, result, **metadata):
        round_data = {
            "player": player,
            "computer": computer,
            "result": result,
            **metadata,
        }
        self.history.append(round_data)
        return round_data

    def remove_last_round(self):
        return self.history.pop() if self.history else None

    def get_history(self):
        return self.history.copy()

    def clear(self):
        self.history.clear()


class GameStack:
    """Stack (LIFO) used to undo the most recently played round."""

    def __init__(self):
        self.stack = []

    def push(self, round_data):
        self.stack.append(round_data)

    def pop(self):
        return self.stack.pop() if self.stack else None

    def is_empty(self):
        return not self.stack

    def clear(self):
        self.stack.clear()


class RecentMovesQueue:
    """FIFO queue that retains only the latest `capacity` rounds."""

    def __init__(self, capacity=5):
        if capacity < 1:
            raise ValueError("Queue capacity must be at least 1.")
        self.capacity = capacity
        self.queue = deque(maxlen=capacity)

    def enqueue(self, round_data):
        self.queue.append(round_data)

    def get_recent_moves(self):
        return list(self.queue)

    def rebuild(self, history):
        self.queue.clear()
        self.queue.extend(history[-self.capacity:])

    def clear(self):
        self.queue.clear()


class ScoreBoard:
    """Dictionary-based score management."""

    def __init__(self):
        self.scores = {"Player": 0, "Computer": 0}

    def update(self, result):
        if result in self.scores:
            self.scores[result] += 1

    def undo(self, result):
        if result in self.scores and self.scores[result] > 0:
            self.scores[result] -= 1

    def get_scores(self):
        return self.scores.copy()

    def reset(self):
        for name in self.scores:
            self.scores[name] = 0
