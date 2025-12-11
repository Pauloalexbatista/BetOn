"""
Test different calendar sources with timeout protection
Tests each source to see which one works best for getting round/jornada data
"""

import requests
from bs4 import BeautifulSoup
import time

# Timeout for each request (seconds)
TIMEOUT = 10

def test_source(name: str, url: str):
    """Test a single source with timeout"""
    print(f"\n{'='*60}")
    print(f"🔍 Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        start = time.time()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elapsed = time.time() - start
        
        print(f"✅ Response received in {elapsed:.2f}s")
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find some key elements
            print(f"\n📊 Page Analysis:")
            print(f"  - Title: {soup.title.string if soup.title else 'N/A'}")
            
            # Look for common table/match structures
            tables = soup.find_all('table')
            divs_match = soup.find_all('div', class_=lambda x: x and 'match' in x.lower())
            
            print(f"  - Tables found: {len(tables)}")
            print(f"  - Match divs found: {len(divs_match)}")
            
            return True
        else:
            print(f"❌ Bad status code: {response.status_code}")
            return False
            
    except requests.Timeout:
        print(f"⏱️ TIMEOUT after {TIMEOUT}s - Site too slow or blocking")
        return False
    except requests.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


def main():
    print("🌐 Testing Calendar Sources for Liga Portugal")
    print("Testing with 10s timeout per source\n")
    
    sources = [
        ("Liga Portugal - Calendário oficial", "https://www.ligaportugal.pt/pt/liga/calendario/"),
        ("Futebol365", "https://www.futebol365.pt/liga-portugal/calendario/"),
        ("A Bola", "https://www.abola.pt/competicoes/ver.aspx?id=1"),
        ("Bola na Rede", "https://www.bolanarede.pt/liga-portugal-betclic/"),
        # ZeroZero last - we know it might be slow
        ("ZeroZero", "https://www.zerozero.pt/competicao/liga-portuguesa"),
    ]
    
    results = {}
    
    for name, url in sources:
        success = test_source(name, url)
        results[name] = success
        time.sleep(2)  # Be polite, wait 2s between requests
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📋 SUMMARY")
    print(f"{'='*60}")
    
    for name, success in results.items():
        status = "✅ Working" if success else "❌ Failed/Timeout"
        print(f"{status:15} - {name}")
    
    print(f"\n{'='*60}")
    print("✅ Test Complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
