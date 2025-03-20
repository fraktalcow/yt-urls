import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

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


def get_channel_id(channel_name: str) -> Optional[str]:
    """Fetch the channel ID for a given channel name.
    
    Args:
        channel_name: The name of the YouTube channel
        
    Returns:
        Channel ID string or None if not found
    """
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
            
        return items[0]['id']['channelId']
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching channel ID for '{channel_name}': {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching channel ID for '{channel_name}': {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Data parsing error for '{channel_name}': {e}")
        
    return None


def fetch_videos(channel_id: str, published_after: Optional[str] = None, max_results: int = 5) -> List[Dict[str, str]]:
    """Fetch videos from a channel ID, optionally filtered by published_after.
    
    Args:
        channel_id: The YouTube channel ID
        published_after: ISO format date string to filter videos published after this date
        max_results: Maximum number of results to return
        
    Returns:
        List of video data dictionaries
    """
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


def main() -> None:
    """Main function to fetch and organize YouTube videos by category."""
    # Define channels by category (channel names as identifiers)
    channels: Dict[str, List[str]] = {
        "Mathematics": ["3Blue1Brown", "Numberphile", "patrickjmt"],
        "Programming": ["realpython", "ThePrimeTimeagen", "MachineLearningStreetTalk"],
        "Philosophy": ["ThePartiallyExaminedLife"],
        "Comedy": ["DailyDoseOfInternet","standupots"]
    }

    # Configurable parameters
    days_back = 7  
    strict_date_filter = True  
    fallback_limit = None  

    # Calculate date filter
    published_after = (datetime.now(timezone.utc) - 
                      timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Calculate fallback date 
    fallback_date = None
    if fallback_limit is not None:
        fallback_date = (datetime.now(timezone.utc) - 
                        timedelta(days=fallback_limit)).strftime("%Y-%m-%dT%H:%M:%SZ")

    
    result: Dict[str, List[Dict[str, str]]] = {}

   
    for category, channel_names in channels.items():
        videos_list = []
        for channel_name in channel_names:
            logger.info(f"Processing channel: {channel_name}")
            
            channel_id = get_channel_id(channel_name)
            if not channel_id:
                logger.warning(f"Skipping channel '{channel_name}' due to error")
                continue
                
            # Fetch videos from the last 'days_back' days
            videos = fetch_videos(channel_id, published_after, max_results=5)
            
            if not videos and not strict_date_filter:
                if fallback_date:
                    logger.info(f"No videos in last {days_back} days for '{channel_name}'. Trying extended range of {fallback_limit} days.")
                    videos = fetch_videos(channel_id, fallback_date, max_results=1)
                else:
                    logger.info(f"No videos in last {days_back} days for '{channel_name}'. Fetching latest video regardless of date.")
                    videos = fetch_videos(channel_id, max_results=1)
                    
            videos_list.extend(videos)
            
        # Sort by publication date (newest first)
        videos_list.sort(key=lambda x: x['publishedAt'], reverse=True)
        result[category] = videos_list

    # Save to JSON file
    try:
        with open('videos.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        logger.info("Videos saved to 'videos.json'")
    except IOError as e:
        logger.error(f"Error saving to videos.json: {e}")


if __name__ == "__main__":
    main()
