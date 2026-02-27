import pandas as pd
import os
import sys
import yaml
from src.utils import load_config

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class EloTracker:
    def __init__(self, k_factor=32, initial_rating=1500):
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings = {} # key: fighter_url (unique), value: {'name': name, 'rating': rating}

    def get_rating(self, fighter_key):
        return self.ratings.get(fighter_key, {'rating': self.initial_rating})['rating']

    def set_rating(self, fighter_key, name, rating):
        self.ratings[fighter_key] = {'name': name, 'rating': rating}

    def expected_score(self, rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(self, fighter_a_key, fighter_a_name, fighter_b_key, fighter_b_name, winner_key):
        rating_a = self.get_rating(fighter_a_key)
        rating_b = self.get_rating(fighter_b_key)

        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = self.expected_score(rating_b, rating_a)

        if winner_key == 'Draw':
            score_a = 0.5
            score_b = 0.5
        elif winner_key == 'NC':
            # No Contest - no rating change
            self.set_rating(fighter_a_key, fighter_a_name, rating_a)
            self.set_rating(fighter_b_key, fighter_b_name, rating_b)
            return rating_a, rating_b
        elif winner_key == fighter_a_key:
            score_a = 1
            score_b = 0
        elif winner_key == fighter_b_key:
            score_a = 0
            score_b = 1
        else:
             # Should not happen ideally
             return rating_a, rating_b

        new_rating_a = rating_a + self.k_factor * (score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (score_b - expected_b)

        self.set_rating(fighter_a_key, fighter_a_name, new_rating_a)
        self.set_rating(fighter_b_key, fighter_b_name, new_rating_b)

        return new_rating_a, new_rating_b

def process_fights(fights_file, output_file):
    if not os.path.exists(fights_file):
        print(f"Fights file not found: {fights_file}")
        return

    config = load_config()
    k_factor = config.get('elo', {}).get('k_factor', 32)
    initial_rating = config.get('elo', {}).get('initial_rating', 1500)

    tracker = EloTracker(k_factor=k_factor, initial_rating=initial_rating)

    df = pd.read_csv(fights_file)

    # Sort by date
    if 'event_date' in df.columns:
        df['event_date'] = pd.to_datetime(df['event_date'])
        df = df.sort_values('event_date')

    print(f"Processing {len(df)} fights for ELO...")

    history = []

    for _, row in df.iterrows():
        fighter_a_name = row['fighter_a']
        fighter_b_name = row['fighter_b']
        # Use URL as unique ID, or fallback to name
        fighter_a_url = row.get('fighter_a_url')
        if pd.isna(fighter_a_url):
            fighter_a_url = fighter_a_name

        fighter_b_url = row.get('fighter_b_url')
        if pd.isna(fighter_b_url):
            fighter_b_url = fighter_b_name

        winner = row['winner']

        if pd.isna(winner):
            continue

        winner_key = None
        if winner == fighter_a_name:
            winner_key = fighter_a_url
        elif winner == fighter_b_name:
            winner_key = fighter_b_url
        elif 'draw' in str(winner).lower():
            winner_key = 'Draw'
        elif 'nc' in str(winner).lower():
            winner_key = 'NC'
        else:
             # Fallback if names don't match exactly?
             if str(winner) in fighter_a_name:
                 winner_key = fighter_a_url
             elif str(winner) in fighter_b_name:
                 winner_key = fighter_b_url
             else:
                 continue

        old_rating_a = tracker.get_rating(fighter_a_url)
        old_rating_b = tracker.get_rating(fighter_b_url)

        new_rating_a, new_rating_b = tracker.update_ratings(
            fighter_a_url, fighter_a_name,
            fighter_b_url, fighter_b_name,
            winner_key
        )

        history.append({
            'date': row['event_date'],
            'fighter_a': fighter_a_name,
            'fighter_b': fighter_b_name,
            'fighter_a_url': fighter_a_url,
            'fighter_b_url': fighter_b_url,
            'winner': winner,
            'rating_a_before': old_rating_a,
            'rating_b_before': old_rating_b,
            'rating_a_after': new_rating_a,
            'rating_b_after': new_rating_b
        })

    # Save current ratings
    ratings_list = []
    for url, data in tracker.ratings.items():
        ratings_list.append({
            'fighter': data['name'],
            'url': url,
            'elo_rating': data['rating']
        })

    ratings_df = pd.DataFrame(ratings_list)

    if not ratings_df.empty:
        ratings_df = ratings_df.sort_values('elo_rating', ascending=False)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    ratings_df.to_csv(output_file, index=False)
    print(f"Saved ELO ratings for {len(ratings_df)} fighters to {output_file}")

    if history:
        history_df = pd.DataFrame(history)
        history_path = output_file.replace('elo_ratings.csv', 'elo_history.csv')
        history_df.to_csv(history_path, index=False)
        print(f"Saved ELO history to {history_path}")

if __name__ == "__main__":
    process_fights('data/raw/fights.csv', 'data/processed/elo_ratings.csv')
