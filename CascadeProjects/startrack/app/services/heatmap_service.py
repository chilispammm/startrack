import io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeatmapService:
    def __init__(self):
        """Initialize the heatmap service with default styles."""
        # Set the style for the plots
        plt.style.use('ggplot')
        sns.set_style("white")
        
    def create_heatmap(
        self, 
        x: list, 
        y: list, 
        title: str = "Player Heatmap",
        cmap: str = 'viridis',
        pitch_color: str = '#22312b',
        line_color: str = '#ffffff',
        figsize: Tuple[int, int] = (10, 7)
    ) -> Optional[bytes]:
        """
        Create a heatmap visualization of player actions on a football pitch.
        
        Args:
            x: List of x-coordinates (0-100 scale)
            y: List of y-coordinates (0-100 scale)
            title: Title for the plot
            cmap: Colormap for the heatmap
            pitch_color: Background color of the pitch
            line_color: Color of pitch lines
            figsize: Figure size (width, height)
            
        Returns:
            Bytes of the generated PNG image or None if error occurs
        """
        if not x or not y:
            logger.warning("No data points provided for heatmap")
            return None
            
        try:
            # Create a figure and axis
            fig, ax = plt.subplots(figsize=figsize)
            
            # Create a pitch
            pitch = Pitch(
                pitch_type='opta',
                pitch_color=pitch_color,
                line_color=line_color,
                stripe=True,
                constrained_layout=True,
                tight_layout=False
            )
            
            # Draw the pitch on the axis
            pitch.draw(ax=ax)
            
            # Convert coordinates if needed (assuming 0-100 scale to 0-120x80)
            x_coords = [xx * 1.2 for xx in x]  # Scale x to 0-120
            y_coords = [yy * 0.8 for yy in y]   # Scale y to 0-80
            
            # Create a 2D histogram of the points
            kde = sns.kdeplot(
                x=x_coords,
                y=y_coords,
                shade=True,
                shade_lowest=False,
                alpha=0.5,
                n_levels=10,
                cmap=cmap,
                ax=ax
            )
            
            # Add scatter plot for individual events
            sns.scatterplot(
                x=x_coords,
                y=y_coords,
                color='red',
                alpha=0.3,
                s=20,
                edgecolor='none',
                ax=ax
            )
            
            # Set title and remove axis labels
            ax.set_title(title, color='white', fontsize=14, pad=20)
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Save the figure to a BytesIO object
            buf = io.BytesIO()
            plt.savefig(
                buf, 
                format='png', 
                dpi=100, 
                bbox_inches='tight',
                facecolor=fig.get_facecolor(),
                transparent=True
            )
            plt.close(fig)
            
            # Return the bytes of the image
            return buf.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            return None

# Create a singleton instance
heatmap_service = HeatmapService()
