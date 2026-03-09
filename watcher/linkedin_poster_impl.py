#!/usr/bin/env python3
"""
LinkedIn Poster Implementation for Personal AI Employee
Scans /Needs_Action for LinkedIn post files and posts them via MCP
"""

import os
import sys
import time
import random
import logging
import shutil
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class LinkedInPoster:
    """LinkedIn Poster that processes posts from Needs_Action folder"""
    
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        self.error_logs_path = self.vault_path / "Error_Logs"
        self.logs_path = self.vault_path / "Logs"
        
        # Ensure directories exist
        for path in [self.done_path, self.error_logs_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration from environment
        self.linkedin_org_urn = os.getenv("LINKEDIN_ORG_URN", "")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.headless = os.getenv("LINKEDIN_HEADLESS", "true").lower() == "true"
        self.dry_run = os.getenv("LINKEDIN_DRY_RUN", "false").lower() == "true"
        
        # Setup logging
        self.logger = self._setup_logging()
        
        self.logger.info("LinkedIn Poster initialized")
        self.logger.info(f"Organization URN: {self.linkedin_org_urn[:20]}..." if self.linkedin_org_urn else "No Organization URN")
        self.logger.info(f"Headless mode: {self.headless}")
        self.logger.info(f"Dry run: {self.dry_run}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("LinkedInPoster")
        logger.setLevel(logging.INFO)
        
        # Create log directory
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # File handler
        log_file = self.logs_path / f"linkedin_poster_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _log_to_markdown(self, message: str, level: str = "INFO"):
        """Log to markdown file for audit trail"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] | LINKEDIN_POSTER | {level} | {message}\n"
        
        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return {}, content
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content
        
        try:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return frontmatter or {}, body
        except yaml.YAMLError as e:
            self.logger.warning(f"Error parsing frontmatter: {e}")
            return {}, content
    
    def _extract_linkedin_posts(self) -> List[Dict[str, Any]]:
        """Scan Needs_Action for LinkedIn post files"""
        posts = []
        
        if not self.needs_action_path.exists():
            self.logger.warning(f"Needs_Action directory not found: {self.needs_action_path}")
            return posts
        
        self.logger.info(f"Scanning {self.needs_action_path} for LinkedIn posts...")
        
        for file_path in self.needs_action_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = self._parse_frontmatter(content)
                
                # Check if this is a LinkedIn post
                post_type = frontmatter.get('type', '')
                
                if post_type == 'linkedin_post':
                    self.logger.info(f"Found LinkedIn post: {file_path.name}")
                    
                    posts.append({
                        'file_path': file_path,
                        'frontmatter': frontmatter,
                        'body': body,
                        'content': frontmatter.get('content', ''),
                        'hashtags': frontmatter.get('hashtags', []),
                        'priority': frontmatter.get('priority', 'medium'),
                        'status': frontmatter.get('status', 'pending')
                    })
                    
            except Exception as e:
                self.logger.error(f"Error reading {file_path.name}: {e}")
                self._log_to_markdown(f"Error reading {file_path.name}: {str(e)}", "ERROR")
        
        self.logger.info(f"Found {len(posts)} LinkedIn post(s) to process")
        return posts
    
    def _post_to_linkedin_mcp(self, content: str, hashtags: List[str] = None) -> Dict[str, Any]:
        """Post to LinkedIn using MCP server"""
        try:
            self.logger.info("Posting to LinkedIn via MCP...")
            
            # Format content with hashtags
            formatted_content = content
            if hashtags:
                hashtag_str = ' '.join(f'#{tag}' for tag in hashtags)
                formatted_content = f"{content}\n\n{hashtag_str}"
            
            if self.dry_run:
                self.logger.info("DRY RUN: Would post to LinkedIn")
                self.logger.info(f"Content: {formatted_content[:200]}...")
                return {
                    'success': True,
                    'post_id': f'dry_run_{int(time.time())}',
                    'url': 'https://www.linkedin.com/feed/',
                    'method': 'dry_run',
                    'content': formatted_content
                }
            
            # Use MCP to post to LinkedIn
            # This calls the MCP server which handles the actual posting
            import subprocess
            
            # Build the MCP command
            mcp_cmd = [
                sys.executable,
                '-m',
                'mcp_servers.linkedin_mcp',
                '--action', 'post',
                '--content', formatted_content
            ]
            
            if self.linkedin_org_urn:
                mcp_cmd.extend(['--org-urn', self.linkedin_org_urn])
            
            # Execute MCP command
            result = subprocess.run(
                mcp_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.info("Successfully posted to LinkedIn via MCP")
                return {
                    'success': True,
                    'post_id': f'mcp_{int(time.time())}',
                    'url': 'https://www.linkedin.com/feed/',
                    'method': 'mcp',
                    'content': formatted_content,
                    'response': result.stdout
                }
            else:
                self.logger.error(f"MCP posting failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr or 'MCP posting failed',
                    'content': formatted_content
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("MCP posting timed out")
            return {
                'success': False,
                'error': 'Posting timed out after 60 seconds',
                'content': content
            }
        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': content
            }
    
    def _move_to_done(self, file_path: Path, result: Dict[str, Any]):
        """Move successfully posted file to Done folder"""
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Append result information
            result_section = f"""
---
## Post Result

**Posted:** {datetime.now().isoformat()}
**Status:** ✅ SUCCESS
**Post ID:** {result.get('post_id', 'N/A')}
**URL:** {result.get('url', 'N/A')}
**Method:** {result.get('method', 'unknown')}
**Content Length:** {len(result.get('content', ''))} characters
"""
            
            updated_content = content + result_section
            
            # Create destination path
            dest_path = self.done_path / file_path.name
            
            # Write updated content to Done folder
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # Remove original file
            file_path.unlink()
            
            self.logger.info(f"Moved {file_path.name} to Done")
            self._log_to_markdown(f"SUCCESS: {file_path.name} posted to LinkedIn", "SUCCESS")
            
        except Exception as e:
            self.logger.error(f"Error moving {file_path.name} to Done: {e}")
            self._log_to_markdown(f"Error moving to Done: {file_path.name} - {str(e)}", "ERROR")
    
    def _move_to_error_logs(self, file_path: Path, result: Dict[str, Any]):
        """Move failed post to Error_Logs folder"""
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Append error information
            error_section = f"""
---
## Post Result

**Attempted:** {datetime.now().isoformat()}
**Status:** ❌ FAILED
**Error:** {result.get('error', 'Unknown error')}
**Content Length:** {len(result.get('content', ''))} characters

## Retry Information
This post failed to publish. Review the error above and retry manually.
"""
            
            updated_content = content + error_section
            
            # Create destination path
            dest_path = self.error_logs_path / file_path.name
            
            # Write updated content to Error_Logs folder
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # Remove original file
            file_path.unlink()
            
            self.logger.error(f"Moved {file_path.name} to Error_Logs")
            self._log_to_markdown(f"FAILED: {file_path.name} - {result.get('error', 'Unknown error')}", "ERROR")
            
        except Exception as e:
            self.logger.error(f"Error moving {file_path.name} to Error_Logs: {e}")
            self._log_to_markdown(f"Error moving to Error_Logs: {file_path.name} - {str(e)}", "ERROR")
    
    def process_linkedin_posts(self) -> Tuple[int, int]:
        """
        Process all LinkedIn posts in Needs_Action folder
        
        Returns:
            Tuple[int, int]: (successful_count, failed_count)
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting LinkedIn Post Processing Cycle")
        self._log_to_markdown("Starting LinkedIn Post Processing Cycle", "INFO")
        
        # Extract posts from Needs_Action
        posts = self._extract_linkedin_posts()
        
        if not posts:
            self.logger.info("No LinkedIn posts to process")
            return 0, 0
        
        successful = 0
        failed = 0
        
        for post in posts:
            file_path = post['file_path']
            content = post['content'] or post['body']
            hashtags = post['hashtags']
            
            self.logger.info("-" * 60)
            self.logger.info(f"Processing: {file_path.name}")
            self.logger.info(f"Content preview: {content[:100]}...")
            self.logger.info(f"Hashtags: {hashtags}")
            
            # Add random delay (5-12 seconds) to avoid rate limiting
            delay = random.uniform(5, 12)
            self.logger.info(f"Waiting {delay:.1f}s before posting...")
            time.sleep(delay)
            
            # Post to LinkedIn via MCP
            result = self._post_to_linkedin_mcp(content, hashtags)
            
            # Handle result
            if result['success']:
                self.logger.info(f"✅ Successfully posted: {file_path.name}")
                self._move_to_done(file_path, result)
                successful += 1
            else:
                self.logger.error(f"❌ Failed to post: {file_path.name}")
                self._move_to_error_logs(file_path, result)
                failed += 1
        
        # Summary
        self.logger.info("=" * 60)
        self.logger.info(f"LinkedIn Post Processing Complete")
        self.logger.info(f"Successful: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Total: {len(posts)}")
        self._log_to_markdown(f"Processing Complete - Success: {successful}, Failed: {failed}", "INFO")
        
        return successful, failed


def main():
    """Main entry point for LinkedIn Poster"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Poster for Personal AI Employee")
    parser.add_argument(
        "--vault-path",
        default="AI_Employee_Vault",
        help="Path to AI Employee vault"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually posting (for testing)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once instead of continuous monitoring"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Polling interval in seconds (default: 300)"
    )
    
    args = parser.parse_args()
    
    # Create poster instance
    poster = LinkedInPoster(vault_path=args.vault_path)
    
    # Override dry_run if specified
    if args.dry_run:
        poster.dry_run = True
        poster.logger.info("Running in DRY RUN mode")
    
    if args.once:
        # Run once
        poster.logger.info("Running single processing cycle...")
        successful, failed = poster.process_linkedin_posts()
        poster.logger.info(f"Cycle complete: {successful} successful, {failed} failed")
    else:
        # Run continuously
        poster.logger.info(f"Starting continuous monitoring (interval: {args.interval}s)...")
        
        try:
            while True:
                successful, failed = poster.process_linkedin_posts()
                poster.logger.info(f"Waiting {args.interval}s before next cycle...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            poster.logger.info("LinkedIn Poster stopped by user")


if __name__ == "__main__":
    main()
