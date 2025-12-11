import requests
from bs4 import BeautifulSoup

def debug_url(round_num):
    url = f"https://www.zerozero.pt/competicao/liga-portuguesa?jornada_in={round_num}"
    print(f"\n--- Debugging Round {round_num}: {url} ---")
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    tables = soup.find_all('table')
    print(f"Tables found: {len(tables)}")
    
    if tables:
        # Check Table 0 (often Standings or Schedule)
        rows = tables[0].find_all('tr')
        print(f"Table 0 Rows: {len(rows)}")
        for i, r in enumerate(rows[:5]):
            print(f"R{i}: {r.get_text(' | ', strip=True)[:80]}")
            
    # Check for div.box_resultados or similar
    results_box = soup.find_all('div', class_='box_resultados')
    print(f"Box Resultados found: {len(results_box)}")

if __name__ == "__main__":
    debug_url(1)
    debug_url(3)
