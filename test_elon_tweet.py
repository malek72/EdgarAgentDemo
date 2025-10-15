"""
Test script for scraping the specific Elon Musk tweet
Tests the specific tweet URL: https://x.com/elonmusk/status/1812258574049157405
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twitter_scraper import TwitterScraper, create_scraper_for_account
import json
from datetime import datetime

def test_elon_musk_tweet():
    """Test scraping the specific Elon Musk tweet"""
    print("🐦 Testing Elon Musk Tweet Scraping")
    print("=" * 60)
    
    # The specific tweet URL you mentioned
    tweet_url = "https://x.com/elonmusk/status/1812258574049157405"
    username = "elonmusk"
    
    try:
        print(f"1. Creating scraper for @{username}...")
        scraper = create_scraper_for_account(username, max_tweets=10)
        print("✅ Scraper created successfully")
        
        print(f"\n2. Testing specific tweet scraping...")
        print(f"   Tweet URL: {tweet_url}")
        
        # Extract tweet ID from URL
        tweet_id = scraper._extract_tweet_id_from_url(tweet_url)
        print(f"   Extracted Tweet ID: {tweet_id}")
        
        # Try to scrape the specific tweet
        tweet_data = scraper.scrape_specific_tweet(tweet_url)
        
        if tweet_data:
            print(f"✅ Successfully scraped specific tweet!")
            print(f"\n📄 Tweet Details:")
            print(f"   Tweet ID: {tweet_data['tweet_id']}")
            print(f"   Username: {tweet_data['username']}")
            print(f"   Content: {tweet_data['content']}")
            print(f"   Created: {tweet_data['created_at']}")
            print(f"   Likes: {tweet_data['favorite_count']}")
            print(f"   Retweets: {tweet_data['retweet_count']}")
            print(f"   Replies: {tweet_data['reply_count']}")
            print(f"   Hashtags: {tweet_data['hashtags']}")
            print(f"   Mentions: {tweet_data['mentions']}")
        else:
            print(f"❌ Failed to scrape specific tweet")
        
        print(f"\n3. Testing general tweet scraping for @{username}...")
        tweets = scraper.scrape_tweets()
        print(f"✅ Scraped {len(tweets)} tweets from @{username}")
        
        if tweets:
            print(f"\n📄 Recent Tweets:")
            for i, tweet in enumerate(tweets[:3], 1):
                print(f"   {i}. {tweet['content'][:100]}...")
                print(f"      ID: {tweet.get('tweet_id', tweet.get('id', 'N/A'))}")
                print(f"      Likes: {tweet['favorite_count']}, RTs: {tweet['retweet_count']}")
                print()
        
        print(f"\n4. Testing complete scraping cycle...")
        result = scraper.run_scraping_cycle()
        print(f"✅ Scraping cycle completed:")
        print(f"   Tweets scraped: {result['tweets_scraped']}")
        print(f"   Tweets saved: {result['tweets_saved']}")
        print(f"   Duration: {result['duration_seconds']:.2f} seconds")
        print(f"   Success: {result['success']}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_tweet_id_extraction():
    """Test tweet ID extraction from various URL formats"""
    print(f"\n🔧 Testing Tweet ID Extraction")
    print("=" * 60)
    
    scraper = create_scraper_for_account("test", max_tweets=1)
    
    test_urls = [
        "https://x.com/elonmusk/status/1812258574049157405",
        "https://twitter.com/elonmusk/status/1812258574049157405",
        "https://x.com/elonmusk/status/1812258574049157405?s=20",
        "https://twitter.com/elonmusk/status/1812258574049157405?ref_src=twsrc%5Etfw",
        "https://x.com/elonmusk/status/1812258574049157405#test"
    ]
    
    for url in test_urls:
        tweet_id = scraper._extract_tweet_id_from_url(url)
        print(f"   URL: {url}")
        print(f"   Extracted ID: {tweet_id}")
        print()

def test_nitter_scraping():
    """Test Nitter scraping capabilities"""
    print(f"\n🌐 Testing Nitter Scraping")
    print("=" * 60)
    
    try:
        scraper = create_scraper_for_account("elonmusk", max_tweets=5)
        
        print("Testing Nitter instances...")
        tweets = scraper._scrape_tweets_nitter()
        
        if tweets:
            print(f"✅ Successfully scraped {len(tweets)} tweets from Nitter")
            for i, tweet in enumerate(tweets[:2], 1):
                print(f"   Tweet {i}: {tweet['content'][:80]}...")
                print(f"   ID: {tweet['id']}, Likes: {tweet['favorite_count']}")
        else:
            print("❌ No tweets found from Nitter")
            
    except Exception as e:
        print(f"❌ Nitter scraping failed: {e}")

if __name__ == "__main__":
    test_elon_musk_tweet()
    test_tweet_id_extraction()
    test_nitter_scraping()
    
    print(f"\n📚 Summary:")
    print(f"The Twitter scraper has been updated to:")
    print(f"1. ✅ Extract tweet IDs from URLs")
    print(f"2. ✅ Scrape specific tweets by URL")
    print(f"3. ✅ Use multiple Nitter instances for real data")
    print(f"4. ✅ Fallback to mock data when scraping fails")
    print(f"5. ✅ Handle various URL formats")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Start the server: python main.py")
    print(f"2. Test the API endpoint for specific tweet scraping")
    print(f"3. Monitor the logs for real scraping attempts")
    print(f"4. Consider using Twitter API for production use")
