import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import requests
from dotenv import load_dotenv
import uvicorn
from user_preferences import UserPreferenceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load API key from environment
load_dotenv()
API_KEY = os.getenv('APIKEY')
if not API_KEY:
    logger.error("No YouTube API key found in environment variables")
    raise ValueError("Missing YouTube API key in environment variables")

BASE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# Create FastAPI app
app = FastAPI(title="YouTube Video Dashboard API")

# Initialize user preferences manager
pref_manager = UserPreferenceManager.initialize_with_defaults()

def get_channels() -> Dict[str, List[str]]:
    return pref_manager.get_channels()

# Cache for channel IDs to reduce API calls
channel_id_cache = {}

def get_channel_id(channel_name: str) -> Optional[str]:
    """Fetch the channel ID for a given channel name."""
    if channel_name in channel_id_cache:
        return channel_id_cache[channel_name]

    params = {
        'part': 'snippet',
        'q': channel_name,
        'type': 'channel',
        'maxResults': 1,
        'key': API_KEY
    }

    try:
        response = requests.get(BASE_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        items = data.get('items', [])

        if not items:
            logger.warning(f"No channel found for '{channel_name}'")
            return None

        channel_id = items[0]['id']['channelId']
        channel_id_cache[channel_name] = channel_id
        return channel_id

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching channel ID for '{channel_name}': {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching channel ID for '{channel_name}': {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Data parsing error for '{channel_name}': {e}")

    return None

def fetch_videos(channel_id: str, published_after: Optional[str] = None, max_results: int = 5) -> List[Dict[str, str]]:
    """Fetch videos from a channel ID, optionally filtered by published_after."""
    params = {
        'part': 'snippet',
        'channelId': channel_id,
        'order': 'date',
        'maxResults': max_results,
        'type': 'video',
        'key': API_KEY
    }

    if published_after:
        params['publishedAfter'] = published_after

    try:
        response = requests.get(BASE_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return [{
            "channel": item['snippet']['channelTitle'],
            "title": item['snippet']['title'],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "publishedAt": item['snippet']['publishedAt']
        } for item in data.get('items', [])]

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching videos for channel ID '{channel_id}': {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching videos for channel ID '{channel_id}': {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Data parsing error for channel ID '{channel_id}': {e}")

    return []

def fetch_all_videos(days_back: int = 7, strict_date_filter: bool = True, fallback_limit: Optional[int] = None) -> Dict[str, List[Dict[str, str]]]:
    """Fetch all videos grouped by category."""
    published_after = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    fallback_date = None
    if fallback_limit is not None:
        fallback_date = (datetime.now(timezone.utc) - timedelta(days=fallback_limit)).strftime("%Y-%m-%dT%H:%M:%SZ")

    channels = get_channels()
    result: Dict[str, List[Dict[str, str]]] = {}

    for category, channel_names in channels.items():
        videos_list = []
        for channel_name in channel_names:
            logger.info(f"Processing channel: {channel_name}")

            channel_id = get_channel_id(channel_name)
            if not channel_id:
                logger.warning(f"Skipping channel '{channel_name}' due to error")
                continue

            videos = fetch_videos(channel_id, published_after, max_results=5)

            if not videos and not strict_date_filter:
                if fallback_date:
                    logger.info(f"No videos in last {days_back} days for '{channel_name}'. Trying extended range of {fallback_limit} days.")
                    videos = fetch_videos(channel_id, fallback_date, max_results=1)
                else:
                    logger.info(f"No videos in last {days_back} days for '{channel_name}'. Fetching latest video regardless of date.")
                    videos = fetch_videos(channel_id, max_results=1)

            videos_list.extend(videos)

        videos_list.sort(key=lambda x: x['publishedAt'], reverse=True)
        result[category] = videos_list

    return result

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css", media_type="text/css")

@app.get("/scripts.js")
async def get_scripts():
    return FileResponse("scripts.js", media_type="application/javascript")

@app.get("/api/refresh", response_class=JSONResponse)
def refresh_videos(days_back: int = 7, strict_filter: bool = True, fallback_days: Optional[int] = None):
    """API endpoint to refresh and save videos to videos.json."""
    try:
        result = fetch_all_videos(days_back, strict_filter, fallback_days)
        with open('videos.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        return {"message": "Videos refreshed and saved to videos.json", "count": sum(len(videos) for videos in result.values())}
    except Exception as e:
        logger.error(f"Error refreshing videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos.json", response_class=JSONResponse)
def get_videos_json():
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    except Exception as e:
        logger.error(f"Error serving videos.json: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    if not os.path.exists('videos.json'):
        try:
            result = fetch_all_videos()
            with open('videos.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
            logger.info("Created initial videos.json file")
        except Exception as e:
            logger.warning(f"Could not create initial videos.json: {e}")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
