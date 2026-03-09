#!/usr/bin/env python3
"""
Meta (Facebook + Instagram) MCP Server - Gold Tier
Posts to Facebook Page and Instagram using Meta Graph API
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
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
        logging.FileHandler(logs_dir / 'meta_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetaGraphAPI:
    """Meta Graph API client for Facebook and Instagram posting"""
    
    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID", "")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET", "")
        self.page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        self.instagram_business_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        
        self.graph_url = "https://graph.facebook.com/v18.0"
        
        logger.info("Meta Graph API client initialized")
        logger.info(f"App ID configured: {'Yes' if self.app_id else 'No'}")
        logger.info(f"Page Access Token: {'Yes' if self.page_access_token else 'No'}")
        logger.info(f"Instagram Business Account: {'Yes' if self.instagram_business_account_id else 'No'}")
    
    def post_to_facebook(self, message: str, link: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Facebook Page
        
        Args:
            message: Post message
            link: Optional link to share
        
        Returns:
            Dict with post data or error
        """
        logger.info(f"Posting to Facebook: {message[:50]}...")
        
        # Get Page ID from access token
        page_id = self._get_page_id()
        
        if not page_id:
            return {"error": "Could not get Page ID. Check PAGE_ACCESS_TOKEN"}
        
        url = f"{self.graph_url}/{page_id}/feed"
        
        params = {
            "message": message,
            "access_token": self.page_access_token
        }
        
        if link:
            params["link"] = link
        
        try:
            response = requests.post(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                
                logger.info(f"Facebook post created: {post_id}")
                
                return {
                    "post_id": post_id,
                    "platform": "facebook",
                    "status": "posted",
                    "url": f"https://facebook.com/{post_id}",
                    "created_at": datetime.now().isoformat()
                }
            else:
                error_data = response.json() if response.text else {}
                logger.error(f"Facebook API error: {response.status_code} - {error_data}")
                
                return {
                    "error": f"Facebook API error: {response.status_code}",
                    "details": error_data.get('error', {}).get('message', str(error_data))
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": f"Request failed: {str(e)}"}
    
    def post_to_instagram(self, caption: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Instagram Business Account
        
        Args:
            caption: Instagram caption
            image_url: Optional image URL (required for photo posts)
        
        Returns:
            Dict with post data or error
        """
        logger.info(f"Posting to Instagram: {caption[:50]}...")
        
        if not self.instagram_business_account_id:
            return {"error": "Instagram Business Account ID not configured"}
        
        if not self.instagram_access_token:
            return {"error": "Instagram Access Token not configured"}
        
        # For now, support text-only posts (Instagram requires media)
        # In production, you'd upload media first
        if not image_url:
            logger.warning("No image URL provided - Instagram requires media")
            return {
                "error": "Instagram requires media (image/video). Please provide image_url"
            }
        
        try:
            # Step 1: Create media container
            container_url = f"{self.graph_url}/{self.instagram_business_account_id}/media"
            
            container_params = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.instagram_access_token
            }
            
            container_response = requests.post(container_url, params=container_params, timeout=30)
            
            if container_response.status_code != 200:
                return {"error": f"Failed to create media container: {container_response.text}"}
            
            container_id = container_response.json().get('id')
            logger.info(f"Instagram media container created: {container_id}")
            
            # Step 2: Publish the media
            publish_url = f"{self.graph_url}/{self.instagram_business_account_id}/media_publish"
            
            publish_params = {
                "creation_id": container_id,
                "access_token": self.instagram_access_token
            }
            
            publish_response = requests.post(publish_url, params=publish_params, timeout=30)
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get('id')
                
                logger.info(f"Instagram post published: {post_id}")
                
                return {
                    "post_id": post_id,
                    "platform": "instagram",
                    "status": "posted",
                    "url": f"https://instagram.com/p/{post_id}",
                    "created_at": datetime.now().isoformat()
                }
            else:
                error_data = publish_response.json() if publish_response.text else {}
                logger.error(f"Instagram API error: {publish_response.status_code} - {error_data}")
                
                return {
                    "error": f"Instagram API error: {publish_response.status_code}",
                    "details": error_data.get('error', {}).get('message', str(error_data))
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": f"Request failed: {str(e)}"}
    
    def post_to_both(self, message: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to both Facebook and Instagram
        
        Args:
            message: Post message/caption
            image_url: Optional image URL for Instagram
        
        Returns:
            Dict with results from both platforms
        """
        logger.info("Posting to both Facebook and Instagram...")
        
        results = {
            "facebook": None,
            "instagram": None,
            "summary": {}
        }
        
        # Post to Facebook
        fb_result = self.post_to_facebook(message)
        results["facebook"] = fb_result
        
        # Post to Instagram (if image provided)
        if image_url:
            ig_result = self.post_to_instagram(message, image_url)
            results["instagram"] = ig_result
        else:
            results["instagram"] = {"status": "skipped", "reason": "No image URL provided"}
        
        # Generate summary
        results["summary"] = self._generate_engagement_summary(results)
        
        return results
    
    def _get_page_id(self) -> Optional[str]:
        """Get Facebook Page ID from access token"""
        url = f"{self.graph_url}/me"
        params = {
            "fields": "id,name",
            "access_token": self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                page_data = response.json()
                return page_data.get('id')
            else:
                logger.error(f"Failed to get Page ID: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting Page ID: {e}")
            return None
    
    def _generate_engagement_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate engagement summary after posting"""
        summary = {
            "total_posts": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "platforms": []
        }
        
        if results.get("facebook") and results["facebook"].get("status") == "posted":
            summary["total_posts"] += 1
            summary["successful_posts"] += 1
            summary["platforms"].append("Facebook")
        
        if results.get("instagram") and results["instagram"].get("status") == "posted":
            summary["total_posts"] += 1
            summary["successful_posts"] += 1
            summary["platforms"].append("Instagram")
        
        if results.get("instagram") and results["instagram"].get("status") == "skipped":
            summary["total_posts"] += 1
            summary["platforms"].append("Instagram (skipped)")
        
        if results.get("facebook") and "error" in results["facebook"]:
            summary["failed_posts"] += 1
        
        if results.get("instagram") and "error" in results["instagram"]:
            summary["failed_posts"] += 1
        
        summary["generated_at"] = datetime.now().isoformat()
        
        return summary
    
    def get_page_insights(self, metric: str = "page_impressions_unique") -> Dict[str, Any]:
        """
        Get Facebook Page insights
        
        Args:
            metric: Insight metric to retrieve
        
        Returns:
            Dict with insights data
        """
        page_id = self._get_page_id()
        
        if not page_id:
            return {"error": "Could not get Page ID"}
        
        url = f"{self.graph_url}/{page_id}/insights"
        params = {
            "metric": metric,
            "access_token": self.page_access_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                insights_data = response.json()
                return {
                    "metric": metric,
                    "data": insights_data.get('data', []),
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                return {"error": f"Failed to get insights: {response.status_code}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


# Global Meta client instance
_meta_client: Optional[MetaGraphAPI] = None


def get_meta_client() -> Optional[MetaGraphAPI]:
    """Get or create Meta client instance"""
    global _meta_client
    
    if _meta_client is None:
        _meta_client = MetaGraphAPI()
    
    return _meta_client


# ============ MCP Tool Functions ============

def meta_post_to_facebook(message: str, link: Optional[str] = None) -> Dict[str, Any]:
    """Post to Facebook Page"""
    try:
        client = get_meta_client()
        if not client:
            return {"error": "Meta client not initialized"}
        
        result = client.post_to_facebook(message, link)
        logger.info(f"Facebook post result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error posting to Facebook: {e}")
        return {"error": str(e)}


def meta_post_to_instagram(caption: str, image_url: Optional[str] = None) -> Dict[str, Any]:
    """Post to Instagram Business Account"""
    try:
        client = get_meta_client()
        if not client:
            return {"error": "Meta client not initialized"}
        
        result = client.post_to_instagram(caption, image_url)
        logger.info(f"Instagram post result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
        return {"error": str(e)}


def meta_post_to_both(message: str, image_url: Optional[str] = None) -> Dict[str, Any]:
    """Post to both Facebook and Instagram"""
    try:
        client = get_meta_client()
        if not client:
            return {"error": "Meta client not initialized"}
        
        result = client.post_to_both(message, image_url)
        logger.info(f"Meta post result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error posting to Meta platforms: {e}")
        return {"error": str(e)}


def meta_get_insights(metric: str = "page_impressions_unique") -> Dict[str, Any]:
    """Get Facebook Page insights"""
    try:
        client = get_meta_client()
        if not client:
            return {"error": "Meta client not initialized"}
        
        result = client.get_page_insights(metric)
        logger.info(f"Insights result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return {"error": str(e)}


# ============ Main Entry Point ============

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Meta (Facebook + Instagram) MCP Server")
    parser.add_argument("--test", action="store_true", help="Test Meta API connection")
    parser.add_argument("--facebook", type=str, help="Post to Facebook")
    parser.add_argument("--instagram", type=str, help="Post to Instagram (requires --image)")
    parser.add_argument("--both", type=str, help="Post to both platforms")
    parser.add_argument("--image", type=str, help="Image URL for Instagram")
    parser.add_argument("--insights", action="store_true", help="Get page insights")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("META (FACEBOOK + INSTAGRAM) MCP SERVER - Gold Tier")
    print("=" * 60)
    
    if args.test:
        print("\n[INFO] Testing Meta API connection...")
        client = get_meta_client()
        
        if client and client.app_id and client.page_access_token:
            print("\n[OK] Meta API client initialized!")
            print(f"   App ID: {'*' * 20}{client.app_id[-5:]}")
            print(f"   Page Access Token: {'Yes' if client.page_access_token else 'No'}")
            print(f"   Instagram Account: {'Yes' if client.instagram_business_account_id else 'No'}")
            
            # Get Page ID to verify
            page_id = client._get_page_id()
            if page_id:
                print(f"\n[OK] Connected to Page ID: {page_id}")
                print("\n[OK] Meta API is working!")
            else:
                print("\n[WARNING] Could not verify Page connection")
        else:
            print("\n[ERROR] Meta credentials not configured!")
            print("[ERROR] Check .env file for FACEBOOK_* variables")
    
    if args.facebook:
        print(f"\n[INFO] Posting to Facebook: {args.facebook[:50]}...")
        result = meta_post_to_facebook(args.facebook)
        
        print("\n" + "=" * 60)
        print("FACEBOOK POST RESULT:")
        print(json.dumps(result, indent=2))
        print("=" * 60)
        
        if result.get("status") == "posted":
            print("\n[OK] Posted to Facebook successfully!")
            print(f"   URL: {result.get('url')}")
        else:
            print(f"\n[ERROR] Failed: {result.get('error', 'Unknown error')}")
    
    if args.instagram:
        if not args.image:
            print("\n[ERROR] Instagram requires --image parameter")
        else:
            print(f"\n[INFO] Posting to Instagram: {args.instagram[:50]}...")
            result = meta_post_to_instagram(args.instagram, args.image)
            
            print("\n" + "=" * 60)
            print("INSTAGRAM POST RESULT:")
            print(json.dumps(result, indent=2))
            print("=" * 60)
            
            if result.get("status") == "posted":
                print("\n[OK] Posted to Instagram successfully!")
            else:
                print(f"\n[ERROR] Failed: {result.get('error', 'Unknown error')}")
    
    if args.both:
        print(f"\n[INFO] Posting to both platforms: {args.both[:50]}...")
        result = meta_post_to_both(args.both, args.image)
        
        print("\n" + "=" * 60)
        print("META POST RESULT:")
        print(json.dumps(result, indent=2))
        print("=" * 60)
        
        summary = result.get("summary", {})
        print(f"\n[SUMMARY]")
        print(f"   Total Posts: {summary.get('total_posts', 0)}")
        print(f"   Successful: {summary.get('successful_posts', 0)}")
        print(f"   Platforms: {', '.join(summary.get('platforms', []))}")
    
    if args.insights:
        print("\n[INFO] Getting page insights...")
        result = meta_get_insights()
        
        print("\n" + "=" * 60)
        print("PAGE INSIGHTS:")
        print(json.dumps(result, indent=2))
        print("=" * 60)
    
    if not (args.test or args.facebook or args.instagram or args.both or args.insights):
        print("\n[INFO] No action specified. Use:")
        print("  --test        Test Meta API connection")
        print("  --facebook    Post to Facebook")
        print("  --instagram   Post to Instagram")
        print("  --both        Post to both platforms")
        print("  --image       Image URL for Instagram")
        print("  --insights    Get page insights")
        print("\nExamples:")
        print('  python meta_mcp.py --test')
        print('  python meta_mcp.py --facebook "Hello Facebook!"')
        print('  python meta_mcp.py --both "Hello both!" --image "https://example.com/image.jpg"')


if __name__ == "__main__":
    main()
