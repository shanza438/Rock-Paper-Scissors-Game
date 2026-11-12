import unittest
from core.game_logic import determine_winner
class TestRules(unittest.TestCase):
    def test_rock_beats_scissors(self): self.assertEqual(determine_winner("rock","scissors"),"Player")
    def test_draw(self): self.assertEqual(determine_winner("paper","paper"),"Draw")
    def test_invalid(self):
        with self.assertRaises(ValueError): determine_winner("fire","rock")
if __name__=="__main__": unittest.main()
