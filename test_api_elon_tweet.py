"""
Test script for the API endpoint to scrape specific Elon Musk tweet
This demonstrates how to use the new API endpoint
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/twitter"

def test_elon_musk_api():
    """Test the API endpoints for Elon Musk tweet scraping"""
    print("🐦 Testing Elon Musk Tweet API")
    print("=" * 60)
    
    username = "elonmusk"
    tweet_url = "https://x.com/elonmusk/status/1812258574049157405"
    
    try:
        # Check if server is running
        print("1. Checking server status...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first:")
            print("   python main.py")
            return
        print("✅ Server is running!")
        
        # Create scraper for Elon Musk
        print(f"\n2. Creating scraper for @{username}...")
        create_data = {
            "username": username,
            "max_tweets": 10,
            "enabled": True
        }
        
        response = requests.post(f"{BASE_URL}/scraper/create", json=create_data)
        if response.status_code == 200:
            print(f"✅ Scraper created for @{username}")
        else:
            print(f"❌ Error creating scraper: {response.text}")
            return
        
        # Test scraping the specific tweet
        print(f"\n3. Testing specific tweet scraping...")
        print(f"   Tweet URL: {tweet_url}")
        
        response = requests.post(f"{BASE_URL}/scraper/{username}/tweet/url", 
                               params={"tweet_url": tweet_url})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully scraped specific tweet!")
            print(f"\n📄 Tweet Details:")
            tweet = result['tweet']
            print(f"   Tweet ID: {tweet['tweet_id']}")
            print(f"   Username: {tweet['username']}")
            print(f"   Content: {tweet['content']}")
            print(f"   Created: {tweet['created_at']}")
            print(f"   Likes: {tweet['favorite_count']}")
            print(f"   Retweets: {tweet['retweet_count']}")
            print(f"   Replies: {tweet['reply_count']}")
            print(f"   Hashtags: {tweet['hashtags']}")
            print(f"   Mentions: {tweet['mentions']}")
        else:
            print(f"❌ Error scraping specific tweet: {response.text}")
        
        # Test running scraper immediately
        print(f"\n4. Testing immediate scraper run...")
        response = requests.post(f"{BASE_URL}/scraper/{username}/run")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scraper run completed:")
            print(f"   Tweets scraped: {result['tweets_scraped']}")
            print(f"   Tweets saved: {result['tweets_saved']}")
            print(f"   Duration: {result['duration_seconds']:.2f} seconds")
            print(f"   Success: {result['success']}")
        else:
            print(f"❌ Error running scraper: {response.text}")
        
        # Get recent tweets
        print(f"\n5. Getting recent tweets...")
        response = requests.get(f"{BASE_URL}/scraper/{username}/tweets?limit=5")
        
        if response.status_code == 200:
            result = response.json()
            tweets = result['tweets']
            print(f"✅ Retrieved {len(tweets)} recent tweets")
            
            if tweets:
                print(f"\n📄 Recent Tweets:")
                for i, tweet in enumerate(tweets[:3], 1):
                    print(f"   {i}. {tweet['content'][:80]}...")
                    print(f"      ID: {tweet.get('tweet_id', 'N/A')}")
                    print(f"      Likes: {tweet['favorite_count']}, RTs: {tweet['retweet_count']}")
                    print()
        else:
            print(f"❌ Error getting tweets: {response.text}")
        
        # Get scraper status
        print(f"\n6. Getting scraper status...")
        response = requests.get(f"{BASE_URL}/scraper/{username}/status")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Scraper Status:")
            print(f"   Username: {status['username']}")
            print(f"   Enabled: {status['enabled']}")
            print(f"   Last run: {status['last_run']}")
            print(f"   Next run: {status['next_run']}")
            print(f"   Total tweets scraped: {status['total_tweets_scraped']}")
        else:
            print(f"❌ Error getting status: {response.text}")
        
        print(f"\n🎉 API testing completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python main.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_tweet_id_extraction_api():
    """Test tweet ID extraction using the API"""
    print(f"\n🔧 Testing Tweet ID Extraction via API")
    print("=" * 60)
    
    username = "testuser"
    test_urls = [
        "https://x.com/elonmusk/status/1812258574049157405",
        "https://twitter.com/elonmusk/status/1812258574049157405",
        "https://x.com/elonmusk/status/1812258574049157405?s=20"
    ]
    
    try:
        # Create a test scraper
        create_data = {
            "username": username,
            "max_tweets": 1,
            "enabled": True
        }
        
        response = requests.post(f"{BASE_URL}/scraper/create", json=create_data)
        if response.status_code != 200:
            print("❌ Could not create test scraper")
            return
        
        for url in test_urls:
            print(f"   Testing URL: {url}")
            response = requests.post(f"{BASE_URL}/scraper/{username}/tweet/url", 
                                   params={"tweet_url": url})
            
            if response.status_code == 200:
                result = response.json()
                tweet_id = result['tweet']['tweet_id']
                print(f"   ✅ Extracted ID: {tweet_id}")
            else:
                print(f"   ❌ Error: {response.text}")
            print()
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_elon_musk_api()
    test_tweet_id_extraction_api()
    
    print(f"\n📚 Summary:")
    print(f"The API now supports:")
    print(f"1. ✅ Creating scrapers for specific accounts")
    print(f"2. ✅ Scraping specific tweets by URL")
    print(f"3. ✅ Running scrapers immediately")
    print(f"4. ✅ Getting recent tweets")
    print(f"5. ✅ Checking scraper status")
    
    print(f"\n🚀 Usage Examples:")
    print(f"# Create scraper")
    print(f"curl -X POST '{BASE_URL}/scraper/create' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"username\": \"elonmusk\", \"max_tweets\": 10, \"enabled\": true}}'")
    print()
    print(f"# Scrape specific tweet")
    print(f"curl -X POST '{BASE_URL}/scraper/elonmusk/tweet/url?tweet_url=https://x.com/elonmusk/status/1812258574049157405'")
    print()
    print(f"# Run scraper immediately")
    print(f"curl -X POST '{BASE_URL}/scraper/elonmusk/run'")
