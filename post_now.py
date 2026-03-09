#!/usr/bin/env python3
"""
Manual LinkedIn Post - Opens browser for manual posting
"""
import os
import sys
import time
from pathlib import Path
import subprocess

# Read the post content
needs_action = Path("AI_Employee_Vault/Needs_Action")
post_file = None

for file_path in needs_action.glob("*.md"):
    post_file = file_path
    break

if post_file:
    with open(post_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract content after frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            post_content = parts[2].strip()

            print("=" * 50)
            print("POST CONTENT TO COPY:")
            print("=" * 50)
            print(post_content)
            print("=" * 50)

            # Open LinkedIn
            print("\nOpening LinkedIn in browser...")
            print("Please manually paste and post the content above.")

            # Open LinkedIn in default browser
            if sys.platform == "win32":
                os.startfile("https://www.linkedin.com/feed/")
            elif sys.platform == "darwin":
                subprocess.run(["open", "https://www.linkedin.com/feed/"])
            else:
                subprocess.run(["xdg-open", "https://www.linkedin.com/feed/"])

            # Wait for user confirmation
            input("\nPress Enter after you have posted the content...")

            # Move to Done
            Path("AI_Employee_Vault/Done").mkdir(exist_ok=True)
            post_file.rename(Path("AI_Employee_Vault/Done") / post_file.name)
            print(f"✅ Moved {post_file.name} to Done folder")
else:
    print("No posts found in Needs_Action folder")