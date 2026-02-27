import unittest
import os
import pandas as pd
from src.data.scraper import scrape_fighters

class TestFighterScraper(unittest.TestCase):
    def test_scrape_fighters(self):
        # Ensure the output directory exists or is clean
        output_file = 'data/raw/fighters.csv'
        if os.path.exists(output_file):
            os.remove(output_file)

        # Run scraper with limit=1 (just 'a')
        scrape_fighters(limit=1)

        # Check if file exists
        self.assertTrue(os.path.exists(output_file))

        # Check if file has content
        df = pd.read_csv(output_file)
        self.assertGreater(len(df), 0)
        self.assertIn('first_name', df.columns)
        self.assertIn('link', df.columns)

if __name__ == '__main__':
    unittest.main()
