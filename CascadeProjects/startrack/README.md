# AFCON 2023 Analytics API

A FastAPI-based backend for AFCON 2023 player valuation and performance analysis. This application provides APIs to access player data, generate heatmaps, and download datasets.

## Features

- **Player Data**: Retrieve player information, valuations, and performance metrics
- **Heatmaps**: Generate visualizations of player actions on the pitch
- **Data Download**: Download complete datasets in CSV format
- **RESTful API**: Well-documented endpoints with Swagger UI
- **Production-ready**: Includes error handling, logging, and CORS support

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd afcon-analytics
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Place your data files in the `app/data/` directory:
   - `afcon_players.csv` - Player data with valuations and metrics
   - `afcon_events.csv` - Event data for heatmap generation

## Running the Application

1. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Players
- `GET /api/v1/players` - List all players with key metrics
- `GET /api/v1/players/{player_id}` - Get detailed information for a specific player
- `GET /api/v1/profile/{player_id}` - (Future) Get player profile with additional data

### Heatmaps
- `GET /api/v1/heatmap/{player_id}?event_type=attack|defense` - Generate a heatmap for a player's actions

### Downloads
- `GET /api/v1/download/players` - Download the complete players dataset
- `GET /api/v1/download/events` - Download the complete events dataset

## Project Structure

```
/app
  ├── main.py              # FastAPI application setup
  ├── routers/             # API endpoints
  │     ├── players.py     # Player-related endpoints
  │     ├── heatmaps.py    # Heatmap generation endpoints
  │     └── downloads.py   # Data download endpoints
  ├── services/            # Business logic
  │     ├── data_loader.py # Data loading and management
  │     └── heatmap_service.py # Heatmap generation logic
  ├── utils/               # Utility functions
  │     └── responses.py   # Custom response formatters
  └── data/                # Data files (not included in version control)
        ├── afcon_players.csv
        └── afcon_events.csv
```

## Development

### Environment Variables
Create a `.env` file in the root directory for environment-specific configurations:

```env
# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Future: API keys for external services
# SPORTSMONKS_API_KEY=your_api_key_here
```

### Running Tests
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Deployment

For production deployment, consider using:
- Gunicorn with Uvicorn workers
- Nginx as a reverse proxy
- Environment variables for configuration
- Process manager (e.g., systemd, Supervisor)

Example production command:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- AFCON 2023 data providers
- FastAPI and Uvicorn teams for the excellent web framework
- mplsoccer for the football pitch visualizations
