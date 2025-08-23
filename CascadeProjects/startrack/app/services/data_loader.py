import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
import logging
import openpyxl
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir: str = "app/data"):
        """Initialize the data loader with the data directory."""
        self.data_dir = Path(data_dir)
        self.players_df = None
        self.events_df = None

        # Unified field mapping
        self.field_mapping = {
            # Identification
            'player_id': ['player_id', 'player id', 'id'],
            'player_name': ['player_name', 'name', 'player name'],
            'team': ['team', 'team_name', 'team name', 'club'],
            'position': ['position', 'pos', 'player_position'],

            # Performance
            'total_minutes_played': ['total_minutes_played', 'minutes', 'mins_played'],
            'matches_played': ['matches_played', 'appearances', 'apps'],
            'total_shots': ['total_shots', 'shots'],
            'total_xg': ['total_xg', 'xg', 'expected_goals'],
            'goal_assists': ['goal_assists', 'assists', 'ast'],
            'shot_assists': ['shot_assists', 'key_passes', 'kp'],
            'total_passes': ['total_passes', 'passes'],
            'completed_passes': ['completed_passes', 'passes_completed'],
            'progressive_passes': ['progressive_passes', 'prog_passes'],
            'passes_into_final_third': ['passes_into_final_third', 'final_third_passes'],
            'passes_into_box': ['passes_into_box', 'box_passes'],
            'total_tackles': ['total_tackles', 'tackles'],
            'total_interceptions': ['total_interceptions', 'interceptions'],
            'total_clearances': ['total_clearances', 'clearances', 'clr'],
            'total_pressures': ['total_pressures', 'pressures'],
            'aerials_won': ['aerials_won', 'aerial_duels_won'],

            # Indices
            'PerformanceIndex': ['performanceindex', 'performance_index'],
            'AfconBoost': ['afconboost', 'afcon_boost'],

            # Valuation
            'CurrentValue': ['currentvalue', 'value', 'market value', 'current_value'],
            'PredictedValue': ['predictedvalue', 'predicted_value'],
            'UndervaluationScore': ['undervaluationscore', 'undervaluation_score'],
            'Undervaluation%': ['undervaluation%', 'undervaluation_percent'],

            # XGB Model Outputs
            'PredictedValueXGB': ['predictedvaluexgb', 'predicted_value_xgb'],
            'UndervaluationScoreXGB': ['undervaluationscorexgb', 'undervaluation_score_xgb'],
            'Undervaluation%XGB': ['undervaluation%xgb', 'undervaluation_percent_xgb'],

            # SportMonks visuals
            'image_url': ['image_url', 'profile_image'],
        }

    def _load_file(self, filename: str) -> pd.DataFrame:
        """Helper method to load a file, automatically detecting the format."""
        file_path = self.data_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def load_data(self) -> Tuple[bool, str]:
        """Load both players and events data from data files."""
        try:
            # Players
            try:
                self.players_df = self._load_file("AFCON_2023_with_predictionsXGB.xlsx")
                logger.info(f"Successfully loaded players data with {len(self.players_df)} records")
            except Exception as e:
                logger.warning(f"Could not load players from Excel, trying CSV: {str(e)}")
                self.players_df = self._load_file("afcon_players.csv")
                logger.info(f"Successfully loaded players data with {len(self.players_df)} records")

            # Events
            try:
                self.events_df = self._load_file("combined_heatmap_df.xlsx")
                logger.info(f"Successfully loaded events data with {len(self.events_df)} records")
            except Exception as e:
                logger.warning(f"Could not load events from Excel, trying CSV: {str(e)}")
                self.events_df = self._load_file("afcon_events.csv")
                logger.info(f"Successfully loaded events data with {len(self.events_df)} records")

            return True, "Data loaded successfully"

        except FileNotFoundError as e:
            error_msg = f"Data file not found: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _get_sportmonks_image(self, player_id: Optional[str]) -> Optional[str]:
        """Stub for SportMonks image integration."""
        if not player_id:
            return None
        return f"https://cdn.sportmonks.com/images/players/{player_id}.png"

    def get_player(self, player_id: str) -> dict:
        """Get a single player's standardized data by ID."""
        if self.players_df is None:
            raise ValueError("Players data not loaded")

        player_data = self.players_df[self.players_df['player_id'] == player_id]
        if player_data.empty:
            return None

        player_dict = player_data.iloc[0].to_dict()
        # Add fallback image
        if "image_url" not in player_dict or pd.isna(player_dict.get("image_url")):
            player_dict["image_url"] = self._get_sportmonks_image(player_id)
        return player_dict

    def get_players_list(self) -> List[Dict[str, Any]]:
        """Get a list of all players with standardized fields."""
        if self.players_df is None:
            raise ValueError("Players data not loaded")

        available_columns = [col.lower() for col in self.players_df.columns]
        selected_fields = {}

        for field, possible_names in self.field_mapping.items():
            for name in possible_names:
                if name.lower() in available_columns:
                    actual_col = next((col for col in self.players_df.columns if col.lower() == name.lower()), None)
                    if actual_col:
                        selected_fields[field] = actual_col
                        break

        if not selected_fields:
            logger.warning("No matching columns found, returning all columns")
            return self.players_df.to_dict('records')

        result = self.players_df[list(selected_fields.values())].copy()
        result.columns = selected_fields.keys()

        # Add SportMonks images where missing
        if "image_url" not in result.columns:
            result["image_url"] = result["player_id"].apply(self._get_sportmonks_image)

        return result.to_dict('records')

    def get_player_events(self, player_id: str, event_type: str = None) -> pd.DataFrame:
        """Get events for a specific player, optionally filtered by event type."""
        if self.events_df is None:
            raise ValueError("Events data not loaded")

        events = self.events_df[self.events_df['player_id'] == player_id].copy()

        if event_type == 'attack':
            attack_events = ['Pass', 'Carry', 'Shot', 'Dribble', 'Ball Receipt*']
            events = events[events['event_type'].isin(attack_events)]
        elif event_type == 'defense':
            defense_events = ['Pressure', 'Interception', 'Block', 'Duel', 'Clearance', 'Ball Recovery']
            events = events[events['event_type'].isin(defense_events)]

        return events

# Singleton
data_loader = DataLoader()
