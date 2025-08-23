from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response
from typing import Optional, Literal
import logging

from app.services.data_loader import data_loader
from app.services.heatmap_service import heatmap_service
from app.utils.responses import image_response, error_response

router = APIRouter(prefix="/api/v1", tags=["heatmaps"])
logger = logging.getLogger(__name__)

@router.get("/heatmap/{player_id}")
async def get_player_heatmap(
    player_id: str,
    event_type: Literal['attack', 'defense'] = 'attack'
) -> Response:
    """
    Generate a heatmap for a specific player's actions.
    
    Args:
        player_id: The ID of the player
        event_type: Type of events to include ('attack' or 'defense')
        
    Returns:
        PNG image of the heatmap
    """
    try:
        # Get player data for the title
        player = data_loader.get_player(player_id)
        if not player:
            return error_response(
                message=f"Player with ID {player_id} not found",
                status_code=404
            )
        
        # Get events for the player
        events_df = data_loader.get_player_events(player_id, event_type)
        
        if events_df.empty:
            return error_response(
                message=f"No {event_type} events found for player {player_id}",
                status_code=404
            )
        
        # Generate heatmap title
        title = f"{player.get('player_name', 'Player')} - {event_type.capitalize()} Heatmap"
        
        # Generate the heatmap
        heatmap_img = heatmap_service.create_heatmap(
            x=events_df['x'].tolist(),
            y=events_df['y'].tolist(),
            title=title,
            cmap='viridis' if event_type == 'attack' else 'YlOrRd'
        )
        
        if not heatmap_img:
            return error_response(
                message="Failed to generate heatmap",
                status_code=500
            )
            
        return image_response(heatmap_img)
        
    except Exception as e:
        logger.error(f"Error generating heatmap: {str(e)}")
        return error_response(
            message="Failed to generate heatmap",
            status_code=500
        )
