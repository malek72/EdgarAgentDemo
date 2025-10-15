"""
Twitter Controller for FastAPI
Handles Twitter scraping endpoints and scheduling
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
import json

# Import the twitter scraper
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twitter_scraper import TwitterScraper, create_scraper_for_account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
route = APIRouter(prefix="/twitter", tags=["Twitter"])

# Global variables for scheduling
scheduler_thread = None
scheduler_running = False
active_scrapers = {}  # Dictionary to store active scrapers by username

# Pydantic models
class ScraperConfig(BaseModel):
    username: str
    max_tweets: int = 50
    enabled: bool = True

class ScrapingResult(BaseModel):
    username: str
    tweets_scraped: int
    tweets_saved: int
    duration_seconds: float
    timestamp: str
    success: bool

class ScraperStatus(BaseModel):
    username: str
    enabled: bool
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    total_tweets_scraped: int = 0

# Background task functions
def run_scheduled_scraping():
    """Run all scheduled scraping tasks"""
    global active_scrapers
    
    logger.info("Running scheduled scraping tasks...")
    
    for username, config in active_scrapers.items():
        if not config.get('enabled', True):
            continue
            
        try:
            scraper = config.get('scraper')
            if scraper:
                result = scraper.run_scraping_cycle()
                logger.info(f"Scheduled scraping completed for {username}: {result}")
                
                # Update last run time
                active_scrapers[username]['last_run'] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"Error in scheduled scraping for {username}: {e}")

def scheduler_worker():
    """Background worker for the scheduler"""
    global scheduler_running
    
    while scheduler_running:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler():
    """Start the background scheduler"""
    global scheduler_thread, scheduler_running
    
    if not scheduler_running:
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        scheduler_thread.start()
        logger.info("Twitter scraper scheduler started")
        
        # Schedule scraping every hour
        schedule.every().hour.do(run_scheduled_scraping)
        logger.info("Scheduled hourly Twitter scraping")

def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler_running
    
    scheduler_running = False
    schedule.clear()
    logger.info("Twitter scraper scheduler stopped")

# API Endpoints

@route.post("/scraper/create", response_model=Dict)
async def create_scraper(config: ScraperConfig):
    """
    Create a new Twitter scraper for a specific account
    
    Args:
        config: Scraper configuration
        
    Returns:
        Dict: Creation result
    """
    try:
        username = config.username.lower().replace('@', '')
        
        # Create scraper instance
        scraper = create_scraper_for_account(username, config.max_tweets)
        
        # Store in active scrapers
        active_scrapers[username] = {
            'scraper': scraper,
            'config': config.dict(),
            'enabled': config.enabled,
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'total_tweets_scraped': 0
        }
        
        # Start scheduler if not running
        if not scheduler_running:
            start_scheduler()
        
        logger.info(f"Created scraper for @{username}")
        
        return {
            "message": f"Scraper created successfully for @{username}",
            "username": username,
            "enabled": config.enabled,
            "max_tweets": config.max_tweets
        }
        
    except Exception as e:
        logger.error(f"Error creating scraper: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating scraper: {str(e)}")

@route.post("/scraper/{username}/run", response_model=ScrapingResult)
async def run_scraper_now(username: str):
    """
    Run scraper immediately for a specific account
    
    Args:
        username: Twitter username
        
    Returns:
        ScrapingResult: Scraping results
    """
    try:
        username = username.lower().replace('@', '')
        
        if username not in active_scrapers:
            raise HTTPException(status_code=404, detail=f"No scraper found for @{username}")
        
        scraper = active_scrapers[username]['scraper']
        result = scraper.run_scraping_cycle()
        
        # Update stats
        active_scrapers[username]['last_run'] = datetime.now().isoformat()
        active_scrapers[username]['total_tweets_scraped'] += result['tweets_scraped']
        
        return ScrapingResult(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running scraper for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error running scraper: {str(e)}")

@route.get("/scraper/{username}/status", response_model=ScraperStatus)
async def get_scraper_status(username: str):
    """
    Get status of a specific scraper
    
    Args:
        username: Twitter username
        
    Returns:
        ScraperStatus: Scraper status information
    """
    try:
        username = username.lower().replace('@', '')
        
        if username not in active_scrapers:
            raise HTTPException(status_code=404, detail=f"No scraper found for @{username}")
        
        scraper_info = active_scrapers[username]
        
        # Calculate next run time (next hour)
        next_run = None
        if scheduler_running:
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            next_run = next_hour.isoformat()
        
        return ScraperStatus(
            username=username,
            enabled=scraper_info['enabled'],
            last_run=scraper_info['last_run'],
            next_run=next_run,
            total_tweets_scraped=scraper_info['total_tweets_scraped']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scraper status for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@route.get("/scraper/{username}/tweets")
async def get_recent_tweets(username: str, limit: int = 10):
    """
    Get recent tweets for a specific account
    
    Args:
        username: Twitter username
        limit: Number of tweets to retrieve
        
    Returns:
        List[Dict]: Recent tweets
    """
    try:
        username = username.lower().replace('@', '')
        
        if username not in active_scrapers:
            raise HTTPException(status_code=404, detail=f"No scraper found for @{username}")
        
        scraper = active_scrapers[username]['scraper']
        tweets = scraper.get_recent_tweets(limit=limit)
        
        return {
            "username": username,
            "tweets": tweets,
            "count": len(tweets)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tweets for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tweets: {str(e)}")

@route.post("/scraper/{username}/tweet/url")
async def scrape_specific_tweet(username: str, tweet_url: str):
    """
    Scrape a specific tweet by URL
    
    Args:
        username: Twitter username
        tweet_url: Full URL of the tweet to scrape
        
    Returns:
        Dict: Tweet data
    """
    try:
        username = username.lower().replace('@', '')
        
        if username not in active_scrapers:
            raise HTTPException(status_code=404, detail=f"No scraper found for @{username}")
        
        scraper = active_scrapers[username]['scraper']
        tweet = scraper.scrape_specific_tweet(tweet_url)
        
        if tweet:
            return {
                "message": f"Successfully scraped tweet from {tweet_url}",
                "tweet": tweet,
                "username": username
            }
        else:
            raise HTTPException(status_code=404, detail=f"Could not scrape tweet from {tweet_url}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping specific tweet for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error scraping tweet: {str(e)}")

@route.put("/scraper/{username}/toggle")
async def toggle_scraper(username: str, enabled: bool):
    """
    Enable or disable a scraper
    
    Args:
        username: Twitter username
        enabled: Whether to enable or disable the scraper
        
    Returns:
        Dict: Toggle result
    """
    try:
        username = username.lower().replace('@', '')
        
        if username not in active_scrapers:
            raise HTTPException(status_code=404, detail=f"No scraper found for @{username}")
        
        active_scrapers[username]['enabled'] = enabled
        
        return {
            "message": f"Scraper for @{username} {'enabled' if enabled else 'disabled'}",
            "username": username,
            "enabled": enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling scraper for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error toggling scraper: {str(e)}")

@route.delete("/scraper/{username}")
async def delete_scraper(username: str):
    """
    Delete a scraper
    
    Args:
        username: Twitter username
        
    Returns:
        Dict: Deletion result
    """
    try:
        username = username.lower().replace('@', '')
        
        if username not in active_scrapers:
            raise HTTPException(status_code=404, detail=f"No scraper found for @{username}")
        
        del active_scrapers[username]
        
        return {
            "message": f"Scraper for @{username} deleted successfully",
            "username": username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scraper for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting scraper: {str(e)}")

@route.get("/scrapers")
async def list_scrapers():
    """
    List all active scrapers
    
    Returns:
        List[ScraperStatus]: List of all scrapers
    """
    try:
        scrapers = []
        
        for username, info in active_scrapers.items():
            # Calculate next run time
            next_run = None
            if scheduler_running and info['enabled']:
                now = datetime.now()
                next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                next_run = next_hour.isoformat()
            
            scrapers.append(ScraperStatus(
                username=username,
                enabled=info['enabled'],
                last_run=info['last_run'],
                next_run=next_run,
                total_tweets_scraped=info['total_tweets_scraped']
            ))
        
        return {
            "scrapers": scrapers,
            "total": len(scrapers),
            "scheduler_running": scheduler_running
        }
        
    except Exception as e:
        logger.error(f"Error listing scrapers: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing scrapers: {str(e)}")

@route.post("/scheduler/start")
async def start_scheduler_endpoint():
    """
    Start the background scheduler
    
    Returns:
        Dict: Start result
    """
    try:
        start_scheduler()
        return {
            "message": "Scheduler started successfully",
            "scheduler_running": scheduler_running
        }
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {str(e)}")

@route.post("/scheduler/stop")
async def stop_scheduler_endpoint():
    """
    Stop the background scheduler
    
    Returns:
        Dict: Stop result
    """
    try:
        stop_scheduler()
        return {
            "message": "Scheduler stopped successfully",
            "scheduler_running": scheduler_running
        }
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {str(e)}")

@route.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get scheduler status
    
    Returns:
        Dict: Scheduler status
    """
    return {
        "scheduler_running": scheduler_running,
        "active_scrapers": len(active_scrapers),
        "enabled_scrapers": len([s for s in active_scrapers.values() if s['enabled']])
    }

# Initialize scheduler on module load
start_scheduler()
