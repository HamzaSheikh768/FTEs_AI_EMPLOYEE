#!/usr/bin/env python3
"""
Twitter API v2 MCP Server - Official API Integration
Posts tweets using Twitter API v2 (no browser automation)
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logs_dir = Path("AI_Employee_Vault/Logs")
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'twitter_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TwitterAPIv2:
    """Twitter API v2 Client for posting tweets using OAuth 1.0a User Context"""
    
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY", "")
        self.api_secret = os.getenv("TWITTER_API_SECRET_KEY", "")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        
        self.api_v2_url = "https://api.twitter.com/2"
        
        # Setup OAuth1 User Context authentication
        self.oauth = OAuth1(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_token_secret,
            signature_method='HMAC-SHA1',
            signature_type='AUTH_HEADER'
        )
        
        logger.info("Twitter API v2 client initialized")
        logger.info(f"OAuth 1.0a configured: Yes")
        logger.info(f"Access Token: {'*' * 20}{self.access_token[-5:] if self.access_token else 'NOT SET'}")
    
    def post_tweet(self, text: str) -> Dict[str, Any]:
        """
        Post a tweet using Twitter API v2 with OAuth 1.0a User Context
        
        Args:
            text: Tweet text (max 280 characters)
        
        Returns:
            Dict with tweet data or error
        """
        logger.info(f"Posting tweet: {text[:50]}...")
        
        # Validate tweet length
        if len(text) > 280:
            return {
                "error": "Tweet text exceeds 280 character limit",
                "length": len(text)
            }
        
        url = f"{self.api_v2_url}/tweets"
        
        payload = {
            "text": text
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            # Post tweet with OAuth 1.0a User Context authentication
            response = requests.post(url, auth=self.oauth, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get('data', {}).get('id')
                tweet_text = result.get('data', {}).get('text')
                
                logger.info(f"Tweet posted successfully: {tweet_id}")
                
                return {
                    "tweet_id": tweet_id,
                    "text": tweet_text,
                    "status": "posted",
                    "url": f"https://twitter.com/i/web/status/{tweet_id}",
                    "created_at": datetime.now().isoformat()
                }
            else:
                error_data = response.json() if response.text else {}
                logger.error(f"Twitter API error: {response.status_code} - {error_data}")
                
                return {
                    "error": f"Twitter API error: {response.status_code}",
                    "details": error_data.get('errors', [{}])[0].get('message', str(error_data)) if error_data else str(response.text)
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "error": f"Request failed: {str(e)}"
            }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information using OAuth 1.0a"""
        logger.info("Getting user info...")
        
        url = f"{self.api_v2_url}/users/me"
        params = {
            "user.fields": "name,username,verified,public_metrics"
        }
        
        try:
            response = requests.get(url, auth=self.oauth, params=params, timeout=30)
            
            if response.status_code == 200:
                user_data = response.json().get('data', {})
                return {
                    "id": user_data.get('id'),
                    "name": user_data.get('name'),
                    "username": user_data.get('username'),
                    "verified": user_data.get('verified', False),
                    "followers": user_data.get('public_metrics', {}).get('followers_count', 0),
                    "following": user_data.get('public_metrics', {}).get('following_count', 0)
                }
            else:
                return {"error": f"Failed to get user info: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


# Global Twitter client instance
_twitter_client: Optional[TwitterAPIv2] = None


def get_twitter_client() -> Optional[TwitterAPIv2]:
    """Get or create Twitter client instance"""
    global _twitter_client
    
    if _twitter_client is None:
        _twitter_client = TwitterAPIv2()
    
    return _twitter_client


# ============ MCP Tool Functions ============

def twitter_post_tweet(text: str) -> Dict[str, Any]:
    """Post a tweet to Twitter"""
    try:
        client = get_twitter_client()
        if not client:
            return {"error": "Twitter client not initialized"}
        
        result = client.post_tweet(text)
        logger.info(f"Tweet result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return {"error": str(e)}


def twitter_get_user_info() -> Dict[str, Any]:
    """Get Twitter user information"""
    try:
        client = get_twitter_client()
        if not client:
            return {"error": "Twitter client not initialized"}
        
        result = client.get_user_info()
        logger.info(f"User info: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return {"error": str(e)}


# ============ Main Entry Point ============

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Twitter API v2 MCP Server")
    parser.add_argument("--test", action="store_true", help="Test Twitter API connection")
    parser.add_argument("--post", type=str, help="Post a tweet")
    parser.add_argument("--user", action="store_true", help="Get user info")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("TWITTER API v2 MCP SERVER - Official API")
    print("=" * 60)
    
    if args.test:
        print("\n[INFO] Testing Twitter API connection...")
        client = get_twitter_client()
        
        if client and client.api_key and client.access_token:
            print("\n[OK] Twitter API v2 client initialized!")
            print(f"   API Key: {'*' * 20}{client.api_key[-5:]}")
            print(f"   Access Token: {'*' * 20}{client.access_token[-5:]}")
            
            # Get user info to verify
            print("\n[INFO] Getting user info...")
            user_info = client.get_user_info()
            
            if 'error' not in user_info:
                print(f"\n[OK] Connected to: @{user_info.get('username')}")
                print(f"   Name: {user_info.get('name')}")
                print(f"   Followers: {user_info.get('followers')}")
                print("\n[OK] Twitter API v2 is working!")
            else:
                print(f"\n[WARNING] Could not verify: {user_info.get('error')}")
                print("[INFO] API credentials are set, but may need verification")
        else:
            print("\n[ERROR] Twitter credentials not configured!")
            print("[ERROR] Check .env file for TWITTER_API_* variables")
    
    if args.post:
        print(f"\n[INFO] Posting tweet: {args.post[:50]}...")
        result = twitter_post_tweet(args.post)
        
        print("\n" + "=" * 60)
        print("RESULT:")
        print(json.dumps(result, indent=2))
        print("=" * 60)
        
        if result.get("status") == "posted":
            print("\n[OK] Tweet posted successfully!")
            print(f"   URL: {result.get('url')}")
        else:
            print(f"\n[ERROR] Failed to post: {result.get('error', 'Unknown error')}")
    
    if args.user:
        print("\n[INFO] Getting user info...")
        result = twitter_get_user_info()
        
        print("\n" + "=" * 60)
        print("USER INFO:")
        print(json.dumps(result, indent=2))
        print("=" * 60)
    
    if not (args.test or args.post or args.user):
        print("\n[INFO] No action specified. Use:")
        print("  --test     Test Twitter API connection")
        print("  --post     Post a tweet")
        print("  --user     Get user info")
        print("\nExample:")
        print('  python twitter_api_v2.py --post "Hello Twitter!"')


if __name__ == "__main__":
    main()
