import pandas as pd
import numpy as np
from pathlib import Path
import os

def generate_sample_players(num_players=100):
    """Generate sample player data"""
    np.random.seed(42)
    
    # Sample data
    teams = ['Algeria', 'Angola', 'Burkina Faso', 'Cameroon', 'Cape Verde', 
             'DR Congo', 'Egypt', 'Equatorial Guinea', 'Gambia', 'Ghana',
             'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Mali', 'Mauritania',
             'Morocco', 'Mozambique', 'Namibia', 'Nigeria', 'Senegal',
             'South Africa', 'Tanzania', 'Tunisia', 'Zambia']
    
    positions = ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST']
    
    data = []
    for i in range(1, num_players + 1):
        current_value = np.random.uniform(0.1, 30)  # In millions
        predicted_value = current_value * np.random.uniform(0.8, 1.5)
        undervaluation = ((predicted_value - current_value) / current_value) * 100
        
        player = {
            'player_id': f'P{i:03d}',
            'player_name': f'Player {i}',
            'team': np.random.choice(teams),
            'position': np.random.choice(positions, p=[0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.1]),
            'age': np.random.randint(18, 36),
            'height_cm': np.random.normal(180, 7),
            'weight_kg': np.random.normal(75, 5),
            'CurrentValue': round(current_value, 2),
            'PredictedValueXGB': round(predicted_value, 2),
            'Undervaluation%XGB': round(undervaluation, 2),
            'minutes_played': np.random.randint(90, 1080),
            'goals': np.random.poisson(3),
            'assists': np.random.poisson(2),
            'pass_accuracy': round(np.random.uniform(70, 95), 1),
            'tackles_per_90': round(np.random.uniform(0.5, 5), 1),
            'interceptions_per_90': round(np.random.uniform(0.5, 4), 1),
            'xg_per_90': round(np.random.uniform(0.1, 0.8), 2),
            'xa_per_90': round(np.random.uniform(0.05, 0.6), 2),
        }
        data.append(player)
    
    return pd.DataFrame(data)

def generate_sample_events(players_df, events_per_player=50):
    """Generate sample event data"""
    np.random.seed(42)
    
    event_types = [
        'Pass', 'Carry', 'Shot', 'Dribble', 'Ball Receipt*',
        'Pressure', 'Interception', 'Block', 'Duel', 'Clearance', 'Ball Recovery'
    ]
    
    data = []
    for _, player in players_df.iterrows():
        player_id = player['player_id']
        team = player['team']
        
        for _ in range(events_per_player):
            event_type = np.random.choice(event_types)
            
            # Generate coordinates based on position
            if player['position'] == 'GK':
                x = np.random.uniform(0, 20)
                y = np.random.uniform(20, 80)
            elif player['position'] in ['CB', 'CDM']:
                x = np.random.uniform(10, 40)
                y = np.random.uniform(10, 90)
            elif player['position'] in ['LB', 'RB']:
                x = np.random.uniform(0, 60)
                y = 10 if player['position'] == 'LB' else 90
                y += np.random.uniform(-10, 10)
            elif player['position'] in ['CM', 'CAM']:
                x = np.random.uniform(30, 70)
                y = np.random.uniform(20, 80)
            elif player['position'] in ['LW', 'RW']:
                x = np.random.uniform(40, 90)
                y = 20 if player['position'] == 'LW' else 80
                y += np.random.uniform(-15, 15)
            else:  # ST
                x = np.random.uniform(60, 100)
                y = np.random.uniform(30, 70)
            
            # Ensure coordinates are within pitch bounds (0-120, 0-80)
            x = max(0, min(120, x))
            y = max(0, min(80, y))
            
            event = {
                'event_id': f"E{len(data)+1:06d}",
                'match_id': f"M{np.random.randint(1, 50):03d}",
                'team': team,
                'player_id': player_id,
                'player_name': player['player_name'],
                'event_type': event_type,
                'x': round(x, 2),
                'y': round(y, 2),
                'minute': np.random.randint(1, 91),
                'second': np.random.randint(0, 60),
                'outcome': np.random.choice(['Successful', 'Unsuccessful', None], p=[0.8, 0.15, 0.05]),
                'timestamp': f"{np.random.randint(1, 6)}'",
            }
            data.append(event)
    
    return pd.DataFrame(data)

def main():
    # Create data directory if it doesn't exist
    data_dir = Path("app/data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate and save sample data
    print("Generating sample players data...")
    players_df = generate_sample_players(200)
    players_df.to_csv(data_dir / "afcon_players.csv", index=False)
    
    print("Generating sample events data...")
    events_df = generate_sample_events(players_df, events_per_player=30)
    events_df.to_csv(data_dir / "afcon_events.csv", index=False)
    
    print(f"Sample data generated successfully in {data_dir.absolute()}")
    print(f"- Players: {len(players_df)}")
    print(f"- Events: {len(events_df)}")

if __name__ == "__main__":
    main()
