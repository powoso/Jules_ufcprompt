# UFC Prediction & Betting Edge System

A Python-based system for collecting UFC fighter stats, calculating ELO ratings, and identifying betting edges in prediction markets.

## Prerequisites

- **Python 3.8+**
- **Git**
- **pip** (Python package installer)

## Installation on macOS

1. **Clone the Repository**
   Open your terminal and clone the project:
   ```bash
   git clone <repository-url>
   cd ufc-prediction-system
   ```

2. **Set up a Virtual Environment**
   It's recommended to use a virtual environment to manage dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Configuration settings are stored in `config/config.yaml`. You can adjust:
- **Base URL**: The source for scraping (default: `http://ufcstats.com`).
- **ELO Settings**:
  - `k_factor`: The sensitivity of rating updates (default: 32).
  - `initial_rating`: Starting ELO for new fighters (default: 1500).

## Usage

To run the full pipeline (scrape data -> process fights -> calculate ELO):

```bash
python main.py
```

This will:
1. Scrape fighter data and save to `data/raw/fighters.csv`.
2. Scrape historical fight results and save to `data/raw/fights.csv`.
3. Calculate current ELO ratings and save to `data/processed/elo_ratings.csv`.
4. Save detailed rating history to `data/processed/elo_history.csv`.

**Note:** The first run may take some time as it scrapes historical data. Subsequent runs will use existing CSV files unless deleted.

## Running Tests

To run the unit tests ensuring the scraper and ELO logic are correct:

```bash
python -m unittest discover tests
```

## Project Structure

```
├── config/             # Configuration files
├── data/               # Data storage (ignored by git)
│   ├── raw/            # Raw scraped CSVs
│   └── processed/      # Processed features & ratings
├── src/                # Source code
│   ├── data/           # Scrapers & data collection
│   ├── features/       # Feature engineering (ELO)
│   └── utils.py        # Shared utilities
├── tests/              # Unit tests
├── main.py             # Pipeline entry point
└── requirements.txt    # Python dependencies
```
