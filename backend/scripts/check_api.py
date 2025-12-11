import requests

def check_api():
    url = "http://localhost:8000/api/matches/filters/options"
    print(f"Checking {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Data received:")
            print(f"Leagues: {data.get('leagues')}")
            print(f"Seasons: {data.get('seasons')}")
            # print(f"Teams count: {len(data.get('teams', []))}")
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_api()
