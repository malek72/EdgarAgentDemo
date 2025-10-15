"""
Twitter Scraper Module for specific account monitoring
Scrapes tweets from a specific Twitter account every hour
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import os
import re
from bs4 import BeautifulSoup
from config.database import supabase_client, BEARERTOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    """
    Twitter scraper for monitoring a specific account
    """
    
    def __init__(self, username: str, max_tweets: int = 50, allow_demo_fallback: bool = False):
        """
        Initialize the Twitter scraper
        
        Args:
            username (str): Twitter username to scrape (without @)
            max_tweets (int): Maximum number of tweets to scrape per run
        """
        self.username = username
        self.max_tweets = max_tweets
        self.last_scraped_id = None
        self.allow_demo_fallback = allow_demo_fallback
        self.setup_database()
    
    def setup_database(self):
        """Setup database table for storing tweets"""
        try:
            # Create tweets table if it doesn't exist
            table_creation_query = """
            CREATE TABLE IF NOT EXISTS tweets (
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
            """
            
            # Create index for better performance
            index_query = """
            CREATE INDEX IF NOT EXISTS idx_tweets_username_created_at 
            ON tweets(username, created_at DESC);
            """
            
            logger.info("Database setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
    
    def get_last_scraped_tweet_id(self) -> Optional[int]:
        """
        Get the last scraped tweet ID for this username
        
        Returns:
            Optional[int]: Last scraped tweet ID or None
        """
        try:
            result = supabase_client.table("tweets")\
                .select("tweet_id")\
                .eq("username", self.username)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]["tweet_id"]
            return None
            
        except Exception as e:
            logger.error(f"Error getting last scraped tweet ID: {e}")
            return None
    
    def scrape_tweets(self, since_id: Optional[int] = None) -> List[Dict]:
        """
        Scrape tweets from the specified account using web scraping
        
        Args:
            since_id (Optional[int]): Only scrape tweets newer than this ID
            
        Returns:
            List[Dict]: List of tweet data dictionaries
        """
        tweets = []
        
        try:
            logger.info(f"Scraping tweets for {self.username}")
            
            # Try multiple scraping methods
            raw_tweets = self._scrape_tweets_web()

            # Normalize to DB schema (ensure tweet_id and consistent fields)
            tweets = [self._process_sample_tweet(t) for t in raw_tweets]
            
            # Filter by since_id if provided
            if since_id and tweets:
                tweets = [t for t in tweets if t.get('tweet_id', 0) > since_id]
            
            logger.info(f"Successfully scraped {len(tweets)} tweets for {self.username}")
            
        except Exception as e:
            logger.error(f"Error scraping tweets for {self.username}: {e}")
        
        return tweets
    
    def scrape_specific_tweet(self, tweet_url: str) -> Optional[Dict]:
        """
        Scrape a specific tweet by URL
        
        Args:
            tweet_url: Full URL of the tweet to scrape
            
        Returns:
            Optional[Dict]: Tweet data or None if failed
        """
        try:
            logger.info(f"Scraping specific tweet: {tweet_url}")
            
            # Extract tweet ID from URL
            tweet_id = self._extract_tweet_id_from_url(tweet_url)
            if not tweet_id:
                logger.error(f"Could not extract tweet ID from URL: {tweet_url}")
                return None
            
            # Try to scrape the specific tweet
            tweet_data = self._scrape_tweet_by_id(tweet_id)
            
            if tweet_data:
                processed_tweet = self._process_sample_tweet(tweet_data)
                logger.info(f"Successfully scraped specific tweet: {tweet_id}")
                return processed_tweet
            else:
                logger.warning(f"Could not scrape tweet {tweet_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping specific tweet: {e}")
            return None
    
    def _extract_tweet_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract tweet ID from Twitter URL
        """
        try:
            # Handle different URL formats
            if '/status/' in url:
                parts = url.split('/status/')
                if len(parts) > 1:
                    tweet_id = parts[1].split('?')[0].split('#')[0]
                    return tweet_id
            return None
        except:
            return None
    
    def _scrape_tweet_by_id(self, tweet_id: str) -> Optional[Dict]:
        """
        Scrape a specific tweet by ID using various methods
        """
        try:
            # Try Nitter first
            tweet_data = self._scrape_tweet_nitter_by_id(tweet_id)
            if tweet_data:
                return tweet_data
            
            # Try alternative methods
            tweet_data = self._scrape_tweet_alternative_by_id(tweet_id)
            if tweet_data:
                return tweet_data
            
            # Fallback to mock data only if enabled
            return self._create_mock_tweet_by_id(tweet_id) if self.allow_demo_fallback else None
            
        except Exception as e:
            logger.error(f"Error scraping tweet by ID {tweet_id}: {e}")
            return None
    
    def _scrape_tweet_nitter_by_id(self, tweet_id: str) -> Optional[Dict]:
        """
        Scrape specific tweet using Nitter
        """
        try:
            nitter_instances = [
                "https://nitter.net",
                "https://nitter.it",
                "https://nitter.1d4.us"
            ]
            
            for instance in nitter_instances:
                try:
                    url = f"{instance}/{self.username}/status/{tweet_id}"
                    logger.info(f"Trying to scrape specific tweet from {url}")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        tweet_data = self._parse_single_nitter_tweet(soup, tweet_id)
                        if tweet_data:
                            logger.info(f"Successfully scraped tweet {tweet_id} from {instance}")
                            return tweet_data
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape tweet {tweet_id} from {instance}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in Nitter tweet scraping: {e}")
        
        return None
    
    def _parse_single_nitter_tweet(self, soup: BeautifulSoup, tweet_id: str) -> Optional[Dict]:
        """
        Parse a single tweet from Nitter HTML
        """
        try:
            # Find the main tweet container
            tweet_container = soup.find('div', class_='tweet-content')
            if not tweet_container:
                return None
            
            # Extract tweet text
            content_elem = tweet_container.find('div', class_='tweet-text')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # Find parent tweet element for metadata
            tweet_elem = tweet_container.find_parent('div', class_='tweet')
            if not tweet_elem:
                return None
            
            # Extract engagement metrics
            stats = tweet_elem.find('div', class_='tweet-stats')
            retweet_count = 0
            favorite_count = 0
            reply_count = 0
            
            if stats:
                stat_links = stats.find_all('a')
                for stat_link in stat_links:
                    text = stat_link.get_text(strip=True)
                    href = stat_link.get('href', '').lower()
                    if 'retweet' in href:
                        retweet_count = self._extract_number(text)
                    elif 'like' in href:
                        favorite_count = self._extract_number(text)
                    elif 'reply' in href:
                        reply_count = self._extract_number(text)
            
            # Extract timestamp
            time_elem = tweet_elem.find('span', class_='tweet-date')
            created_at = datetime.now()
            if time_elem and time_elem.get('title'):
                try:
                    created_at = datetime.fromisoformat(time_elem['title'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', content)
            mentions = re.findall(r'@\w+', content)
            
            return {
                "id": tweet_id,
                "content": content,
                "created_at": created_at,
                "retweet_count": retweet_count,
                "favorite_count": favorite_count,
                "reply_count": reply_count,
                "quote_count": 0,
                "is_retweet": False,
                "is_quote_tweet": False,
                "language": "en",
                "hashtags": hashtags,
                "mentions": mentions,
                "urls": []
            }
            
        except Exception as e:
            logger.error(f"Error parsing single Nitter tweet: {e}")
            return None
    
    def _scrape_tweet_alternative_by_id(self, tweet_id: str) -> Optional[Dict]:
        """
        Alternative method to scrape specific tweet
        """
        # This would implement alternative scraping methods
        # For now, return None to use fallback
        return None
    
    def _create_mock_tweet_by_id(self, tweet_id: str) -> Dict:
        """
        Create mock tweet data for specific tweet ID (for demonstration)
        """
        logger.info(f"Creating mock tweet data for ID: {tweet_id}")
        
        return {
            "id": tweet_id,
            "content": f"Mock tweet content for {self.username} (ID: {tweet_id}). This is demonstration data since real scraping failed. The actual tweet from {self.username} could not be retrieved due to Twitter's anti-scraping measures.",
            "created_at": datetime.now(),
            "retweet_count": 150,
            "favorite_count": 500,
            "reply_count": 25,
            "quote_count": 10,
            "is_retweet": False,
            "is_quote_tweet": False,
            "language": "en",
            "hashtags": ["demo", "mock"],
            "mentions": [],
            "urls": [],
            "demo": True
        }
    
    def _scrape_tweets_web(self) -> List[Dict]:
        """
        Scrape real tweets using web scraping from Twitter/X
        """
        tweets = []
        
        try:
            # Use multiple methods to get real tweets
            tweets = (
                self._scrape_tweets_nitter()
                or self._scrape_tweets_nitter_rss()
                or self._scrape_tweets_alternative()
            )
            
            if not tweets:
                if self.allow_demo_fallback:
                    logger.warning(f"No tweets found for {self.username}, using fallback method (demo)")
                    tweets = self._scrape_tweets_fallback()
                else:
                    logger.warning(f"No tweets found for {self.username}; demo fallback disabled, returning empty list")
                    tweets = []
                
        except Exception as e:
            logger.error(f"Error in web scraping: {e}")
            # Fallback to sample data only if enabled
            if self.allow_demo_fallback:
                tweets = self._scrape_tweets_fallback()
            else:
                tweets = []
        
        return tweets
    
    def _scrape_tweets_nitter(self) -> List[Dict]:
        """
        Scrape tweets using Nitter (Twitter frontend alternative)
        """
        tweets = []
        
        try:
            # Updated Nitter instances (some may be down)
            nitter_instances = [
                "https://nitter.net",
                "https://nitter.it",
                "https://nitter.cz",
                "https://nitter.fdn.fr",
                "https://nitter.1d4.us"
            ]
            
            for instance in nitter_instances:
                try:
                    url = f"{instance}/{self.username}"
                    logger.info(f"Trying to scrape from {url}")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        tweets = self._parse_nitter_tweets(soup)
                        if tweets:
                            logger.info(f"Successfully scraped {len(tweets)} tweets from {instance}")
                            break
                        else:
                            logger.warning(f"No tweets found from {instance}")
                    else:
                        logger.warning(f"HTTP {response.status_code} from {instance}")
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape from {instance}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in Nitter scraping: {e}")
        
        return tweets

    def _scrape_tweets_nitter_rss(self) -> List[Dict]:
        """
        Scrape tweets using Nitter RSS/Atom feeds as a fallback.
        """
        tweets: List[Dict] = []
        try:
            nitter_instances = [
                "https://nitter.net",
                "https://nitter.it",
                "https://nitter.cz",
                "https://nitter.fdn.fr",
                "https://nitter.1d4.us",
            ]

            for instance in nitter_instances:
                for feed_suffix in ("rss", "atom"):
                    try:
                        url = f"{instance}/{self.username}/{feed_suffix}"
                        logger.info(f"Trying RSS from {url}")
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        }
                        response = requests.get(url, headers=headers, timeout=15)
                        if response.status_code != 200:
                            logger.warning(f"HTTP {response.status_code} from {url}")
                            continue

                        soup = BeautifulSoup(response.content, 'xml')
                        items = soup.find_all(['item', 'entry'])
                        for i, item in enumerate(items[: self.max_tweets]):
                            title = (item.title.text if item.find('title') else '').strip()
                            desc_tag = item.find('description') or item.find('content')
                            description = (desc_tag.text if desc_tag else '').strip()
                            link_tag = item.find('link')
                            link = ''
                            if link_tag:
                                # Atom may have href, RSS has text
                                link = link_tag.get('href') or link_tag.text or ''
                            pub_date_tag = item.find('pubDate') or item.find('updated')
                            created_at = datetime.now()
                            if pub_date_tag and pub_date_tag.text:
                                try:
                                    # Best-effort parse; many feeds are RFC2822/ISO8601
                                    created_at = datetime.fromisoformat(pub_date_tag.text.replace('Z', '+00:00'))
                                except Exception:
                                    pass

                            # Extract ID from link
                            tweet_id = None
                            if '/status/' in link:
                                try:
                                    tweet_id = link.split('/status/')[-1].split('?')[0].split('#')[0]
                                except Exception:
                                    tweet_id = None
                            if not tweet_id:
                                tweet_id = str(int(time.time() * 1000) + i)

                            content = title or description
                            hashtags = re.findall(r'#\w+', content)
                            mentions = re.findall(r'@\w+', content)

                            tweets.append({
                                "id": tweet_id,
                                "content": content,
                                "created_at": created_at,
                                "retweet_count": 0,
                                "favorite_count": 0,
                                "reply_count": 0,
                                "quote_count": 0,
                                "is_retweet": False,
                                "is_quote_tweet": False,
                                "language": "en",
                                "hashtags": hashtags,
                                "mentions": mentions,
                                "urls": [link] if link else [],
                            })

                        if tweets:
                            logger.info(f"Successfully scraped {len(tweets)} tweets via RSS from {instance}")
                            return tweets
                    except Exception as e:
                        logger.warning(f"Failed RSS from {instance}/{feed_suffix}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error in Nitter RSS scraping: {e}")
        return tweets
    
    def _parse_nitter_tweets(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parse tweets from Nitter HTML
        """
        tweets = []
        
        try:
            # Find tweet containers
            tweet_containers = soup.find_all('div', class_='tweet-content')
            
            for i, container in enumerate(tweet_containers[:self.max_tweets]):
                try:
                    # Extract tweet text
                    content_elem = container.find('div', class_='tweet-text')
                    content = content_elem.get_text(strip=True) if content_elem else ""
                    
                    # Extract tweet metadata
                    tweet_elem = container.find_parent('div', class_='tweet')
                    if not tweet_elem:
                        continue
                    
                    # Extract tweet ID from data attributes or links
                    tweet_link = tweet_elem.find('a', class_='tweet-link')
                    tweet_id = None
                    if tweet_link and tweet_link.get('href'):
                        href = tweet_link['href']
                        tweet_id = href.split('/')[-1] if '/' in href else None
                    
                    if not tweet_id:
                        tweet_id = int(time.time() * 1000) + i
                    
                    # Extract engagement metrics
                    stats = tweet_elem.find('div', class_='tweet-stats')
                    retweet_count = 0
                    favorite_count = 0
                    reply_count = 0
                    
                    if stats:
                        stat_links = stats.find_all('a')
                        for stat_link in stat_links:
                            text = stat_link.get_text(strip=True)
                            if 'retweet' in stat_link.get('href', '').lower():
                                retweet_count = self._extract_number(text)
                            elif 'like' in stat_link.get('href', '').lower():
                                favorite_count = self._extract_number(text)
                            elif 'reply' in stat_link.get('href', '').lower():
                                reply_count = self._extract_number(text)
                    
                    # Extract timestamp
                    time_elem = tweet_elem.find('span', class_='tweet-date')
                    created_at = datetime.now()
                    if time_elem and time_elem.get('title'):
                        try:
                            created_at = datetime.fromisoformat(time_elem['title'].replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Extract hashtags and mentions
                    hashtags = re.findall(r'#\w+', content)
                    mentions = re.findall(r'@\w+', content)
                    
                    tweet_data = {
                        "id": tweet_id,
                        "content": content,
                        "created_at": created_at,
                        "retweet_count": retweet_count,
                        "favorite_count": favorite_count,
                        "reply_count": reply_count,
                        "quote_count": 0,
                        "is_retweet": False,
                        "is_quote_tweet": False,
                        "language": "en",
                        "hashtags": hashtags,
                        "mentions": mentions,
                        "urls": []
                    }
                    
                    tweets.append(tweet_data)
                    
                except Exception as e:
                    logger.warning(f"Error parsing tweet {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Nitter tweets: {e}")
        
        return tweets
    
    def _scrape_tweets_alternative(self) -> List[Dict]:
        """
        Alternative scraping method using different approach
        """
        tweets = []
        
        try:
            # Try using a different approach - search for recent tweets
            search_url = f"https://twitter.com/search?q=from%3A{self.username}&src=typed_query&f=live"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            if response.status_code == 200:
                # This is a simplified approach - in reality, Twitter's frontend is complex
                # and requires JavaScript rendering or API access
                logger.info("Alternative scraping method attempted")
                
        except Exception as e:
            logger.error(f"Error in alternative scraping: {e}")
        
        return tweets
    
    def _scrape_tweets_fallback(self) -> List[Dict]:
        """
        Fallback method with sample data when real scraping fails
        """
        logger.info(f"Using fallback method for {self.username}")
        
        sample_tweets = [
            {
                "id": int(time.time() * 1000) + i,
                "content": f"Sample tweet {i+1} from {self.username} - This is a demonstration tweet. Real scraping failed, using fallback data.",
                "created_at": datetime.now() - timedelta(hours=i),
                "retweet_count": i * 10,
                "favorite_count": i * 25,
                "reply_count": i * 5,
                "quote_count": i * 2,
                "is_retweet": False,
                "is_quote_tweet": False,
                "language": "en",
                "hashtags": [f"sample{i+1}", "demo", "fallback"],
                "mentions": [],
                "urls": [],
                "demo": True
            }
            for i in range(min(3, self.max_tweets))
        ]
        
        return sample_tweets
    
    def _extract_number(self, text: str) -> int:
        """
        Extract number from text like "1.2K", "5M", "123"
        """
        try:
            text = text.strip().upper()
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            elif 'B' in text:
                return int(float(text.replace('B', '')) * 1000000000)
            else:
                return int(''.join(filter(str.isdigit, text)) or 0)
        except:
            return 0
    
    def _process_sample_tweet(self, tweet_data: Dict) -> Dict:
        """
        Process sample tweet data into structured format
        
        Args:
            tweet_data: Sample tweet data dictionary
            
        Returns:
            Dict: Processed tweet data
        """
        return {
            "tweet_id": tweet_data["id"],
            "username": self.username,
            "content": tweet_data["content"],
            "created_at": tweet_data["created_at"].isoformat(),
            "retweet_count": tweet_data["retweet_count"],
            "favorite_count": tweet_data["favorite_count"],
            "reply_count": tweet_data["reply_count"],
            "quote_count": tweet_data["quote_count"],
            "is_retweet": tweet_data["is_retweet"],
            "is_quote_tweet": tweet_data["is_quote_tweet"],
            "language": tweet_data["language"],
            "hashtags": tweet_data["hashtags"],
            "mentions": tweet_data["mentions"],
            "urls": tweet_data["urls"],
            "scraped_at": datetime.now().isoformat(),
            "raw_data": {
                "id": tweet_data["id"],
                "url": f"https://twitter.com/{self.username}/status/{tweet_data['id']}",
                "user": {
                    "username": self.username,
                    "displayname": self.username.title(),
                    "verified": False
                },
                "demo": bool(tweet_data.get("demo", False))
            }
        }
    
    def _process_tweet(self, tweet_data: Dict) -> Dict:
        """
        Process raw tweet data into structured format
        
        Args:
            tweet_data: Raw tweet data dictionary
            
        Returns:
            Dict: Processed tweet data
        """
        # This method is kept for compatibility but now expects a dictionary
        return self._process_sample_tweet(tweet_data)
    
    def save_tweets(self, tweets: List[Dict]) -> bool:
        """
        Save tweets to database
        
        Args:
            tweets (List[Dict]): List of tweet data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not tweets:
            return True
        
        try:
            # Filter out demo tweets if present
            filtered = [t for t in tweets if not t.get("raw_data", {}).get("demo")]

            if not filtered:
                logger.info("No real tweets to save (demo tweets filtered out)")
                return True

            # Insert tweets into database
            result = supabase_client.table("tweets").insert(filtered).execute()
            
            if result.data:
                logger.info(f"Successfully saved {len(filtered)} tweets to database")
                return True
            else:
                logger.error("Failed to save tweets to database")
                return False
                
        except Exception as e:
            logger.error(f"Error saving tweets to database: {e}")
            return False
    
    def run_scraping_cycle(self) -> Dict:
        """
        Run a complete scraping cycle
        
        Returns:
            Dict: Summary of scraping results
        """
        start_time = datetime.now()
        logger.info(f"Starting scraping cycle for {self.username}")
        
        # Get last scraped tweet ID
        last_id = self.get_last_scraped_tweet_id()
        
        # Scrape new tweets
        tweets = self.scrape_tweets(since_id=last_id)
        
        # Save tweets to database
        saved = False
        if tweets:
            saved = self.save_tweets(tweets)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "username": self.username,
            "tweets_scraped": len(tweets),
            "tweets_saved": len(tweets) if saved else 0,
            "duration_seconds": duration,
            "timestamp": end_time.isoformat(),
            "success": saved
        }
        
        logger.info(f"Scraping cycle completed: {result}")
        return result
    
    def get_recent_tweets(self, limit: int = 10) -> List[Dict]:
        """
        Get recent tweets from database
        
        Args:
            limit (int): Number of recent tweets to retrieve
            
        Returns:
            List[Dict]: List of recent tweets
        """
        try:
            result = supabase_client.table("tweets")\
                .select("*")\
                .eq("username", self.username)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting recent tweets: {e}")
            return []


def create_scraper_for_account(username: str, max_tweets: int = 50) -> TwitterScraper:
    """
    Factory function to create a Twitter scraper for a specific account
    
    Args:
        username (str): Twitter username to monitor
        max_tweets (int): Maximum tweets per scraping cycle
        
    Returns:
        TwitterScraper: Configured scraper instance
    """
    return TwitterScraper(username, max_tweets)


# Example usage and testing
if __name__ == "__main__":
    # Example: Create scraper for a specific account
    scraper = create_scraper_for_account("elonmusk", max_tweets=20)
    
    # Run one scraping cycle
    result = scraper.run_scraping_cycle()
    print(f"Scraping result: {result}")
    
    # Get recent tweets
    recent_tweets = scraper.get_recent_tweets(limit=5)
    print(f"Recent tweets: {len(recent_tweets)} found")
