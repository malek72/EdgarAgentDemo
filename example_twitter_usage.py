"""
Example usage of the Twitter Scraper
This script demonstrates how to use the Twitter scraper system
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/twitter"

def create_scraper(username: str, max_tweets: int = 50):
    """Create a new Twitter scraper"""
    url = f"{BASE_URL}/scraper/create"
    data = {
        "username": username,
        "max_tweets": max_tweets,
        "enabled": True
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"✅ Scraper created for @{username}")
        return response.json()
    else:
        print(f"❌ Error creating scraper: {response.text}")
        return None

def run_scraper_now(username: str):
    """Run scraper immediately"""
    url = f"{BASE_URL}/scraper/{username}/run"
    response = requests.post(url)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Scraping completed for @{username}")
        print(f"   Tweets scraped: {result['tweets_scraped']}")
        print(f"   Tweets saved: {result['tweets_saved']}")
        print(f"   Duration: {result['duration_seconds']:.2f} seconds")
        return result
    else:
        print(f"❌ Error running scraper: {response.text}")
        return None

def get_scraper_status(username: str):
    """Get scraper status"""
    url = f"{BASE_URL}/scraper/{username}/status"
    response = requests.get(url)
    if response.status_code == 200:
        status = response.json()
        print(f"📊 Status for @{username}:")
        print(f"   Enabled: {status['enabled']}")
        print(f"   Last run: {status['last_run']}")
        print(f"   Next run: {status['next_run']}")
        print(f"   Total tweets scraped: {status['total_tweets_scraped']}")
        return status
    else:
        print(f"❌ Error getting status: {response.text}")
        return None

def get_recent_tweets(username: str, limit: int = 5):
    """Get recent tweets"""
    url = f"{BASE_URL}/scraper/{username}/tweets?limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"🐦 Recent tweets for @{username}:")
        for i, tweet in enumerate(data['tweets'], 1):
            print(f"   {i}. {tweet['content'][:100]}...")
            print(f"      Created: {tweet['created_at']}")
            print(f"      Likes: {tweet['favorite_count']}, RTs: {tweet['retweet_count']}")
            print()
        return data
    else:
        print(f"❌ Error getting tweets: {response.text}")
        return None

def list_all_scrapers():
    """List all active scrapers"""
    url = f"{BASE_URL}/scrapers"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"📋 Active scrapers ({data['total']}):")
        for scraper in data['scrapers']:
            print(f"   @{scraper['username']} - {'Enabled' if scraper['enabled'] else 'Disabled'}")
            print(f"      Last run: {scraper['last_run']}")
            print(f"      Total tweets: {scraper['total_tweets_scraped']}")
            print()
        return data
    else:
        print(f"❌ Error listing scrapers: {response.text}")
        return None

def get_scheduler_status():
    """Get scheduler status"""
    url = f"{BASE_URL}/scheduler/status"
    response = requests.get(url)
    if response.status_code == 200:
        status = response.json()
        print(f"⏰ Scheduler Status:")
        print(f"   Running: {status['scheduler_running']}")
        print(f"   Active scrapers: {status['active_scrapers']}")
        print(f"   Enabled scrapers: {status['enabled_scrapers']}")
        return status
    else:
        print(f"❌ Error getting scheduler status: {response.text}")
        return None

def main():
    """Main example function"""
    print("🐦 Twitter Scraper Example")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first:")
            print("   python main.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python main.py")
        return
    
    print("✅ Server is running!")
    print()
    
    # Example usernames to scrape
    usernames = ["elonmusk", "openai", "github"]
    
    # Create scrapers
    print("1. Creating scrapers...")
    for username in usernames:
        create_scraper(username, max_tweets=20)
        time.sleep(1)  # Small delay between requests
    
    print()
    
    # Check scheduler status
    print("2. Checking scheduler status...")
    get_scheduler_status()
    print()
    
    # Run scrapers immediately
    print("3. Running scrapers immediately...")
    for username in usernames:
        run_scraper_now(username)
        time.sleep(2)  # Small delay between requests
    print()
    
    # Get recent tweets
    print("4. Getting recent tweets...")
    for username in usernames:
        get_recent_tweets(username, limit=3)
        time.sleep(1)
    print()
    
    # List all scrapers
    print("5. Listing all scrapers...")
    list_all_scrapers()
    print()
    
    print("🎉 Example completed!")
    print("\nThe scrapers will now run automatically every hour.")
    print("You can check the status anytime using the API endpoints.")

if __name__ == "__main__":
    main()
