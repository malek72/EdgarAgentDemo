"""
Simple test script for the Twitter Scraper
This script demonstrates the basic functionality without requiring a running server
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twitter_scraper import TwitterScraper, create_scraper_for_account
import json
from datetime import datetime

def test_twitter_scraper():
    """Test the Twitter scraper functionality"""
    print("🐦 Testing Twitter Scraper")
    print("=" * 50)
    
    try:
        # Create a scraper for a test account
        username = "testuser"
        print(f"1. Creating scraper for @{username}...")
        scraper = create_scraper_for_account(username, max_tweets=3)
        print("✅ Scraper created successfully")
        
        # Test scraping tweets
        print(f"\n2. Testing tweet scraping for @{username}...")
        tweets = scraper.scrape_tweets()
        print(f"✅ Scraped {len(tweets)} tweets")
        
        # Display sample tweets
        print(f"\n3. Sample tweets:")
        for i, tweet in enumerate(tweets, 1):
            print(f"   Tweet {i}:")
            print(f"   Content: {tweet['content']}")
            print(f"   Created: {tweet['created_at']}")
            print(f"   Likes: {tweet['favorite_count']}, RTs: {tweet['retweet_count']}")
            print(f"   Hashtags: {tweet['hashtags']}")
            print()
        
        # Test running a complete cycle
        print("4. Testing complete scraping cycle...")
        result = scraper.run_scraping_cycle()
        print(f"✅ Scraping cycle completed:")
        print(f"   Tweets scraped: {result['tweets_scraped']}")
        print(f"   Tweets saved: {result['tweets_saved']}")
        print(f"   Duration: {result['duration_seconds']:.2f} seconds")
        print(f"   Success: {result['success']}")
        
        print(f"\n🎉 All tests passed! The Twitter scraper is working correctly.")
        print(f"\nNote: This is a demonstration with sample data.")
        print(f"For real Twitter data, you would need to:")
        print(f"1. Set up proper Twitter API credentials")
        print(f"2. Configure your Supabase database")
        print(f"3. Start the FastAPI server with: python main.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_scraper_configuration():
    """Test different scraper configurations"""
    print("\n🔧 Testing Scraper Configurations")
    print("=" * 50)
    
    # Test different configurations
    configs = [
        {"username": "user1", "max_tweets": 5},
        {"username": "user2", "max_tweets": 10},
        {"username": "user3", "max_tweets": 1}
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n{i}. Testing configuration: {config}")
        try:
            scraper = create_scraper_for_account(config["username"], config["max_tweets"])
            tweets = scraper.scrape_tweets()
            print(f"   ✅ Created scraper for @{config['username']}")
            print(f"   ✅ Scraped {len(tweets)} tweets (max: {config['max_tweets']})")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_twitter_scraper()
    test_scraper_configuration()
    
    print(f"\n📚 Next Steps:")
    print(f"1. Start the server: python main.py")
    print(f"2. Test the API endpoints using the example script")
    print(f"3. Configure your database credentials in .env")
    print(f"4. Set up real Twitter API access for production use")
