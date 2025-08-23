import requests
import json
import time
import os
from pathlib import Path

def test_api():
    base_url = "http://localhost:8000/api/v1"
    
    print("Testing API endpoints...\n")
    
    # Test 1: Get all players
    print("1. Testing GET /players")
    response = requests.get(f"{base_url}/players")
    print(f"Status: {response.status_code}")
    players = response.json()
    print(f"Players returned: {len(players.get('data', {}).get('players', []))}")
    print("-" * 50)
    
    if not players.get('data', {}).get('players'):
        print("No players found. Make sure the server is running and data is loaded.")
        return
    
    # Get a sample player ID for further tests
    sample_player = players['data']['players'][0]
    player_id = sample_player['player_id']
    player_name = sample_player['player_name']
    
    # Test 2: Get single player
    print(f"\n2. Testing GET /players/{player_id}")
    response = requests.get(f"{base_url}/players/{player_id}")
    print(f"Status: {response.status_code}")
    player_data = response.json()
    print(f"Player: {player_name} (ID: {player_id})")
    print(f"Details: {json.dumps(player_data['data']['player'], indent=2)}")
    print("-" * 50)
    
    # Test 3: Generate attack heatmap
    print(f"\n3. Testing GET /heatmap/{player_id}?event_type=attack")
    response = requests.get(f"{base_url}/heatmap/{player_id}?event_type=attack")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        output_path = Path("heatmap_attack.png")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Heatmap saved to {output_path.absolute()}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)
    
    # Test 4: Generate defense heatmap
    print(f"\n4. Testing GET /heatmap/{player_id}?event_type=defense")
    response = requests.get(f"{base_url}/heatmap/{player_id}?event_type=defense")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        output_path = Path("heatmap_defense.png")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Heatmap saved to {output_path.absolute()}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)
    
    # Test 5: Download events
    print("\n5. Testing GET /download/events")
    response = requests.get(f"{base_url}/download/events")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        output_path = Path("downloaded_events.csv")
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Events data saved to {output_path.absolute()}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)
    
    # Test 6: Health check
    print("\n6. Testing GET /health")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    import sys
    
    # Check if the server is running
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
        if response.status_code != 200:
            print("Server is not responding. Please start the server first.")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("Server is not running. Please start the server first.")
        print("You can start it with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    test_api()
