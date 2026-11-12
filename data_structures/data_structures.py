from collections import deque
class GameHistory:
    def __init__(self): self.history=[]
    def add_round(self,player,computer,result,**metadata):
        item={"player":player,"computer":computer,"result":result,**metadata}; self.history.append(item); return item
    def remove_last_round(self): return self.history.pop() if self.history else None
    def get_history(self): return self.history.copy()
    def clear(self): self.history.clear()
class GameStack:
    def __init__(self): self.stack=[]
    def push(self,item): self.stack.append(item)
    def pop(self): return self.stack.pop() if self.stack else None
    def is_empty(self): return not self.stack
    def clear(self): self.stack.clear()
class RecentMovesQueue:
    def __init__(self,capacity=5):
        if capacity<1: raise ValueError("Capacity must be positive.")
        self.capacity=capacity; self.queue=deque(maxlen=capacity)
    def enqueue(self,item): self.queue.append(item)
    def get_recent_moves(self): return list(self.queue)
    def rebuild(self,items): self.queue.clear(); self.queue.extend(items[-self.capacity:])
    def clear(self): self.queue.clear()
class ScoreBoard:
    def __init__(self): self.scores={"Player":0,"Computer":0}
    def update(self,result):
        if result in self.scores: self.scores[result]+=1
    def get_scores(self): return self.scores.copy()
    def reset(self): self.scores={"Player":0,"Computer":0}
