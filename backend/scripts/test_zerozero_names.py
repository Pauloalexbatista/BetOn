import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.zerozero.pt/competicao/liga-portuguesa?jornada_in=14" # Testing a recent round

def test_fetch():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Fetching {URL}...")
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        match_table = soup.find('table', class_='zztable')
        if not match_table:
            print("No table found")
            return

        rows = match_table.find_all('tr')[1:]
        print(f"\nMatches found:")
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                match_text = cells[1].get_text(strip=True)
                print(f"Raw Text: {match_text}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch()
