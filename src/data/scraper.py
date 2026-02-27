import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import os
import time
import sys
from datetime import datetime
from src.utils import load_config

CONFIG = load_config()
BASE_URL = CONFIG['base_url']

def scrape_fighters(limit=None):
    """
    Scrapes fighter data from ufcstats.com.

    Args:
        limit (int): Optional limit on the number of pages (characters a-z) to scrape.
                     If provided, only scrapes the first `limit` characters.
    """
    all_fighters = []
    # Loop through a-z
    chars = list(string.ascii_lowercase)

    if limit:
        chars = chars[:limit]

    print(f"Scraping fighters for characters: {chars}")

    for char in chars:
        url = f"{BASE_URL}/statistics/fighters?char={char}&page=all"
        print(f"Fetching {url}...")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # The table rows are inside the tbody
        rows = soup.select('table.b-statistics__table tbody tr')

        if not rows:
             print(f"No rows found for {char}")
             continue

        # Sometimes the first row is empty or weird, let's just iterate
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 10:
                continue

            # Columns:
            # 0: First Name, 1: Last Name, 2: Nickname, 3: Ht, 4: Wt, 5: Reach, 6: Stance, 7: W, 8: L, 9: D, 10: Belt?

            first_name = cols[0].get_text(strip=True)
            last_name = cols[1].get_text(strip=True)
            nickname = cols[2].get_text(strip=True)
            height = cols[3].get_text(strip=True)
            weight = cols[4].get_text(strip=True)
            reach = cols[5].get_text(strip=True)
            stance = cols[6].get_text(strip=True)
            win = cols[7].get_text(strip=True)
            loss = cols[8].get_text(strip=True)
            draw = cols[9].get_text(strip=True)

            link_tag = cols[0].find('a')
            link = link_tag['href'] if link_tag else None

            all_fighters.append({
                'first_name': first_name,
                'last_name': last_name,
                'nickname': nickname,
                'height': height,
                'weight': weight,
                'reach': reach,
                'stance': stance,
                'wins': win,
                'losses': loss,
                'draws': draw,
                'link': link
            })

        time.sleep(1) # Be nice

    df = pd.DataFrame(all_fighters)

    output_path = os.path.join('data', 'raw', 'fighters.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} fighters to {output_path}")


def scrape_completed_events(limit=None):
    """
    Scrapes completed UFC events.
    """
    events_url = f"{BASE_URL}/statistics/events/completed?page=all"
    print(f"Fetching events list from {events_url}...")

    try:
        response = requests.get(events_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching events list: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # The table is class b-statistics__table-events
    # But let's select more broadly
    event_rows = soup.select('table.b-statistics__table-events tbody tr')

    if not event_rows:
        # Fallback to previous selector if class changed
        event_rows = soup.select('table.b-statistics__table tbody tr')

    events_to_scrape = []

    # Check for empty rows or just header
    for row in event_rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue

        link_tag = cols[0].find('a')
        if not link_tag:
            continue

        event_name = link_tag.get_text(strip=True)
        event_link = link_tag['href']
        # The date is in a span inside the first td
        date_span = cols[0].find('span')
        event_date_str = date_span.get_text(strip=True) if date_span else ""
        location = cols[1].get_text(strip=True)

        # Only add past events
        # The date format seems to be "February 28, 2026"
        try:
            event_date = datetime.strptime(event_date_str, "%B %d, %Y")
            if event_date > datetime.now():
                continue
        except ValueError:
            pass # Keep it if we can't parse, or skip? Let's keep it.

        events_to_scrape.append({
            'name': event_name,
            'link': event_link,
            'date': event_date_str,
            'location': location
        })

    if limit:
        events_to_scrape = events_to_scrape[:limit]

    print(f"Found {len(events_to_scrape)} events. Scraping fights...")

    all_fights = []

    for event in events_to_scrape:
        print(f"Scraping event: {event['name']} ({event['date']})")
        try:
            resp = requests.get(event['link'])
            resp.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch event {event['name']}: {e}")
            continue

        event_soup = BeautifulSoup(resp.content, 'html.parser')
        fight_rows = event_soup.select('table.b-fight-details__table tbody tr')

        for f_row in fight_rows:
            cols = f_row.find_all('td')
            if len(cols) < 10:
                continue

            # Fighter Names
            fighter_ps = cols[1].find_all('p')
            if len(fighter_ps) < 2:
                continue

            fighter_a_name = fighter_ps[0].get_text(strip=True)
            fighter_b_name = fighter_ps[1].get_text(strip=True)

            fighter_a_link = fighter_ps[0].find('a')['href'] if fighter_ps[0].find('a') else None
            fighter_b_link = fighter_ps[1].find('a')['href'] if fighter_ps[1].find('a') else None

            # Outcomes
            outcome_ps = cols[0].find_all('p')
            if len(outcome_ps) < 2:
                # Should not happen for a valid fight row
                continue

            outcome_a = outcome_ps[0].get_text(strip=True)
            outcome_b = outcome_ps[1].get_text(strip=True)

            winner = None
            if outcome_a == 'win':
                winner = fighter_a_name
            elif outcome_b == 'win':
                winner = fighter_b_name
            elif 'draw' in outcome_a.lower() or 'draw' in outcome_b.lower():
                winner = 'Draw'
            else:
                winner = 'NC' # No Contest / NC

            # Other stats
            weight_class = cols[6].get_text(strip=True)
            method = cols[7].get_text(strip=True)
            round_num = cols[8].get_text(strip=True)
            time_str = cols[9].get_text(strip=True)

            all_fights.append({
                'event_name': event['name'],
                'event_date': event['date'],
                'fighter_a': fighter_a_name,
                'fighter_b': fighter_b_name,
                'winner': winner,
                'method': method,
                'round': round_num,
                'time': time_str,
                'weight_class': weight_class,
                'fighter_a_url': fighter_a_link,
                'fighter_b_url': fighter_b_link
            })

        time.sleep(0.5)

    df = pd.DataFrame(all_fights)
    # Parse date
    try:
        df['event_date'] = pd.to_datetime(df['event_date'])
    except Exception as e:
        print(f"Warning: Could not parse dates: {e}")

    output_path = os.path.join('data', 'raw', 'fights.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} fights to {output_path}")

if __name__ == "__main__":
    # Scrape more events to ensure we get past events
    scrape_completed_events(limit=30)
