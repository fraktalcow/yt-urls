# YouTube Video Dashboard

A web-based dashboard that automatically fetches and categorizes recent YouTube videos from specified channels.

![Preview of the dashboard](assets/pre.png)

## Features

- Fetches recent videos from categorized YouTube channels
- Organizes videos by topic categories
- Displays video information in a clean, modern UI
- Configurable date range filter for video freshness
- Fallback options for channels with no recent uploads

## How It Works

1. The Python script (`main.py`) uses the YouTube Data API to fetch videos
2. Videos are organized by categories and saved to `videos.json`
3. The web interface loads this data and presents it in a user-friendly dashboard

## Setup

### Prerequisites

- Python 3.6+
- YouTube Data API key

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install requests python-dotenv
   ```
3. Create a `.env` file with your YouTube API key:
   ```
   APIKEY=your_youtube_api_key_here
   ```

## Usage

1. Run the Python script to fetch the latest videos:
   ```
   python main.py
   ```
2. Open `index.html` in your browser to view the dashboard

## Configuration

Edit the `channels` dictionary in `main.py` to customize your video sources:

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
