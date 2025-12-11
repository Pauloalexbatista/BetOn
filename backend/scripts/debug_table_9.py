import requests
from bs4 import BeautifulSoup

def debug_table_9():
    url = "https://www.zerozero.pt/competicao/liga-portuguesa?jornada_in=3"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"Fetching {url}...")
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    tables = soup.find_all('table')
    if len(tables) > 9:
        t = tables[9] # Check Table 9
        print("Table 9 Content:")
        rows = t.find_all('tr')
        for i, r in enumerate(rows[:10]):
            print(f"Row {i}: {r.get_text(' | ', strip=True)}")
    else:
        print("Table 9 not found")

    if len(tables) > 8:
        t = tables[8]
        print("\nTable 8 Content:")
        rows = t.find_all('tr')
        for i, r in enumerate(rows[:5]):
           print(f"Row {i}: {r.get_text(' | ', strip=True)}")

if __name__ == "__main__":
    debug_table_9()
