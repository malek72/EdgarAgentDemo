# Twitter Scraper System

A comprehensive Twitter scraping system that monitors specific Twitter accounts and scrapes their tweets every hour. Built with FastAPI, Supabase, and snscrape.

## Features

- **Hourly Scraping**: Automatically scrapes tweets from specified accounts every hour
- **Real-time API**: FastAPI endpoints for managing scrapers and viewing data
- **Database Storage**: Stores tweets in Supabase with full metadata
- **Background Scheduling**: Runs scraping tasks in the background
- **RESTful API**: Complete REST API for managing scrapers
- **Error Handling**: Robust error handling and logging
- **Incremental Scraping**: Only scrapes new tweets since last run

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables in `.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DB_CONNECTION=supabase
```

3. Start the server:
```bash
python main.py
```

## API Endpoints

### Scraper Management

- `POST /twitter/scraper/create` - Create a new scraper
- `GET /twitter/scraper/{username}/status` - Get scraper status
- `POST /twitter/scraper/{username}/run` - Run scraper immediately
- `PUT /twitter/scraper/{username}/toggle` - Enable/disable scraper
- `DELETE /twitter/scraper/{username}` - Delete scraper
- `GET /twitter/scrapers` - List all scrapers

### Data Access

- `GET /twitter/scraper/{username}/tweets` - Get recent tweets
- `GET /twitter/scheduler/status` - Get scheduler status

### Scheduler Control

- `POST /twitter/scheduler/start` - Start background scheduler
- `POST /twitter/scheduler/stop` - Stop background scheduler

## Usage Examples

### 1. Create a Scraper

```python
import requests

# Create a scraper for @elonmusk
response = requests.post("http://localhost:8000/twitter/scraper/create", json={
    "username": "elonmusk",
    "max_tweets": 50,
    "enabled": True
})
```

### 2. Run Scraper Immediately

```python
# Run scraper for @elonmusk immediately
response = requests.post("http://localhost:8000/twitter/scraper/elonmusk/run")
result = response.json()
print(f"Scraped {result['tweets_scraped']} tweets")
```

### 3. Get Recent Tweets

```python
# Get last 10 tweets for @elonmusk
response = requests.get("http://localhost:8000/twitter/scraper/elonmusk/tweets?limit=10")
tweets = response.json()['tweets']
```

### 4. Check Scraper Status

```python
# Get status of @elonmusk scraper
response = requests.get("http://localhost:8000/twitter/scraper/elonmusk/status")
status = response.json()
print(f"Enabled: {status['enabled']}")
print(f"Last run: {status['last_run']}")
```

## Database Schema

The system creates a `tweets` table with the following structure:

```sql
CREATE TABLE tweets (
    id BIGSERIAL PRIMARY KEY,
    tweet_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    retweet_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    is_retweet BOOLEAN DEFAULT FALSE,
    is_quote_tweet BOOLEAN DEFAULT FALSE,
    language VARCHAR(10),
    hashtags TEXT[],
    mentions TEXT[],
    urls TEXT[],
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_data JSONB
);
```

## Configuration

### Scraper Configuration

Each scraper can be configured with:

- `username`: Twitter username (without @)
- `max_tweets`: Maximum tweets to scrape per run
- `enabled`: Whether the scraper is active

### Scheduler Configuration

- Scrapers run every hour automatically
- Background scheduler starts when the first scraper is created
- Scheduler can be started/stopped via API

## Example Script

Run the example script to see the system in action:

```bash
python example_twitter_usage.py
```

This will:
1. Create scrapers for popular accounts
2. Run them immediately
3. Display recent tweets
4. Show scraper status

## Logging

The system logs all activities to:
- Console output
- `twitter_scraper.log` file

Log levels include INFO, WARNING, and ERROR.

## Error Handling

The system includes comprehensive error handling:
- Network errors during scraping
- Database connection issues
- Invalid usernames
- Rate limiting (handled gracefully)

## Monitoring

Monitor your scrapers using:
- API endpoints for real-time status
- Log files for detailed activity
- Database queries for data analysis

## Troubleshooting

### Common Issues

1. **Server not starting**: Check if port 8000 is available
2. **Database errors**: Verify Supabase credentials in `.env`
3. **Scraping failures**: Check internet connection and Twitter availability
4. **Scheduler not running**: Restart the server or use the start scheduler endpoint

### Debug Mode

Enable debug logging by modifying the logging level in `twitter_scraper.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Store API keys securely in environment variables
- Use HTTPS in production
- Implement authentication for production use
- Monitor API usage and implement rate limiting

## Performance

- Scrapers run in background threads
- Database operations are optimized with indexes
- Incremental scraping reduces data transfer
- Configurable batch sizes for different use cases
