from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
import os
import logging
from pathlib import Path

router = APIRouter(prefix="/api/v1", tags=["downloads"])
logger = logging.getLogger(__name__)

@router.get("/download/events")
async def download_events():
    """
    Download the complete events dataset as a CSV file.
    
    Returns:
        CSV file containing all events data
    """
    try:
        file_path = Path("app/data/afcon_events.csv")
        
        if not file_path.exists():
            logger.error(f"Events file not found at {file_path}")
            raise HTTPException(
                status_code=404,
                detail="Events data file not found"
            )
            
        return FileResponse(
            path=file_path,
            filename="afcon_events.csv",
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=afcon_events.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading events file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download events file"
        )

@router.get("/download/players")
async def download_players():
    """
    Download the complete players dataset as a CSV file.
    
    Returns:
        CSV file containing all players data
    """
    try:
        file_path = Path("app/data/afcon_players.csv")
        
        if not file_path.exists():
            logger.error(f"Players file not found at {file_path}")
            raise HTTPException(
                status_code=404,
                detail="Players data file not found"
            )
            
        return FileResponse(
            path=file_path,
            filename="afcon_players.csv",
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=afcon_players.csv"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading players file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download players file"
        )
