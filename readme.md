# YouTube Video Dashboard

A web-based dashboard that automatically fetches and categorizes recent YouTube videos from specified channels.

![Preview of the dashboard](assets/pre.png)

## Features

- Fetches recent videos from categorized YouTube channels
- Organizes videos by topic categories
- Displays video information in a clean, modern UI
- Configurable date range filter for video freshness
- Fallback options for channels with no recent uploads
- FastAPI server for dynamic data fetching and serving

## How It Works

### Traditional Mode
1. The Python script (`main.py`) uses the YouTube Data API to fetch videos
2. Videos are organized by categories and saved to `videos.json`
3. Open `index.html` in your browser to view the static dashboard

### FastAPI Mode (Recommended)
1. The FastAPI server (`main.py`) handles both API requests and serves the UI
2. Videos are fetched on demand or refreshed via the UI
3. Access the dashboard by visiting `http://localhost:8000` in your browser

## Setup

### Prerequisites

- Python 3.6+
- YouTube Data API key

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install requests python-dotenv fastapi uvicorn aiofiles
   ```
3. Create a `.env` file with your YouTube API key:
   ```
   APIKEY=your_youtube_api_key_here
   ```

## Usage

### Traditional Mode
1. Run the Python script to fetch the latest videos:
   ```
   python main.py
   ```
2. Open `index.html` in your browser to view the dashboard

### FastAPI Mode
1. Start the FastAPI server:
   ```
   python main_two.py
   ```
2. Open `http://localhost:8000` in your browser
3. Use the refresh button to fetch new videos

## API Endpoints

When running in FastAPI mode, the following API endpoints are available:

- `GET /api/videos` - Get all videos organized by category
- `GET /api/refresh` - Refresh videos and save to videos.json
- `GET /videos.json` - Serve the videos.json file (for backward compatibility)

Query parameters for `/api/videos` and `/api/refresh`:
- `days_back` - Number of days to look back for videos (default: 7)
- `strict_filter` - Whether to use strict date filtering (default: true)
- `fallback_days` - Extended days range for fallback videos (default: null)

## Configuration

Edit the `channels` dictionary in `main.py` or `main_two.py` to customize your video sources:

```python
channels = {
    "Mathematics": ["3Blue1Brown", "Numberphile", "patrickjmt"],
    "Programming": ["realpython", "ThePrimeTimeagen", "MachineLearningStreetTalk"],
    "Philosophy": ["ThePartiallyExaminedLife"],
    "Comedy": ["DailyDoseOfInternet","standupots"]
}
```

## License

See the [LICENSE](LICENSE) file for details.
