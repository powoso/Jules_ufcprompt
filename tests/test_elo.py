import unittest
import pandas as pd
import os
from src.features.elo import EloTracker

class TestElo(unittest.TestCase):
    def test_elo_calculation(self):
        tracker = EloTracker(k_factor=32, initial_rating=1500)

        # Test Case 1: Equal ratings, A wins
        # Expected score = 0.5
        # New Rating A = 1500 + 32 * (1 - 0.5) = 1516
        # New Rating B = 1500 + 32 * (0 - 0.5) = 1484

        # update_ratings signature: (fighter_a_key, fighter_a_name, fighter_b_key, fighter_b_name, winner_key)
        new_a, new_b = tracker.update_ratings("url_a", "Fighter A", "url_b", "Fighter B", "url_a")
        self.assertEqual(new_a, 1516)
        self.assertEqual(new_b, 1484)

    def test_draw(self):
        tracker = EloTracker(k_factor=32, initial_rating=1500)
        new_a, new_b = tracker.update_ratings("url_a", "Fighter A", "url_b", "Fighter B", "Draw")
        self.assertEqual(new_a, 1500)
        self.assertEqual(new_b, 1500)

    def test_nc(self):
        tracker = EloTracker(k_factor=32, initial_rating=1500)
        new_a, new_b = tracker.update_ratings("url_a", "Fighter A", "url_b", "Fighter B", "NC")
        self.assertEqual(new_a, 1500)
        self.assertEqual(new_b, 1500)

if __name__ == '__main__':
    unittest.main()
