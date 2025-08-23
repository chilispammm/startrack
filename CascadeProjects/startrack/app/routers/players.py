from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from app.services.data_loader import data_loader
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/api/v1", tags=["players"])
logger = logging.getLogger(__name__)

@router.get("/players", response_model=Dict[str, Any])
async def get_players() -> Dict[str, Any]:
    """
    Get a list of all players with key metrics.
    
    Returns:
        List of players with selected fields:
        - player_id
        - player_name
        - team
        - position
        - CurrentValue
        - PredictedValueXGB
        - Undervaluation%XGB
    """
    try:
        players = data_loader.get_players_list()
        return success_response(
            data={"players": players},
            message="Players retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting players: {str(e)}")
        return error_response(
            message="Failed to retrieve players",
            status_code=500
        )

@router.get("/players/{player_id}", response_model=Dict[str, Any])
async def get_player(player_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific player.
    
    Args:
        player_id: The ID of the player to retrieve
        
    Returns:
        Complete player data including all available metrics
    """
    try:
        player = data_loader.get_player(player_id)
        if not player:
            return error_response(
                message=f"Player with ID {player_id} not found",
                status_code=404
            )
            
        return success_response(
            data={"player": player},
            message="Player details retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting player {player_id}: {str(e)}")
        return error_response(
            message=f"Failed to retrieve player {player_id}",
            status_code=500
        )

# Stub for future SportsMonks API integration
@router.get("/profile/{player_id}", response_model=Dict[str, Any])
async def get_player_profile(player_id: str) -> Dict[str, Any]:
    """
    Stub endpoint for future SportsMonks API integration.
    Currently returns a placeholder response.
    """
    return success_response(
        data={
            "player_id": player_id,
            "profile": "Player profile data will be available soon",
            "source": "SportsMonks API (coming soon)"
        },
        message="Player profile endpoint stub"
    )
