"""
MCP Server for LinkedIn Poster functionality
Exposes LinkedIn posting capabilities as MCP tools
"""
import importlib.util
import sys
import json
import asyncio
import traceback
import argparse

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from fastmcp import FastMCP
from fastmcp.tools import Tool
from pydantic import BaseModel, Field

import tempfile


class LinkedInPostRequest(BaseModel):
    """Request parameters for creating a LinkedIn post"""
    content: str = Field(description="The content of the LinkedIn post")
    hashtags: List[str] = Field(default=[], description="Hashtags to include in the post")
    post_type: str = Field(default="update", description="Type of post (update, article, etc.)")


class LinkedInPostResponse(BaseModel):
    """Response model for LinkedIn post creation"""
    success: bool
    post_id: str
    message: str


def create_linkedin_post_draft_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for creating a LinkedIn post draft"""
    content = request.get("content", "")
    hashtags = request.get("hashtags", [])
    post_type = request.get("post_type", "update")

    try:
        # Import the LinkedInPoster class from the watcher directory
        spec = importlib.util.spec_from_file_location(
            "linkedin_poster_impl",
            str(Path.cwd() / "watcher" / "linkedin_poster_impl.py")
        )
        if spec is None or spec.loader is None:
            raise ImportError("Failed to load module spec for linkedin_poster_impl")
        linkedin_poster_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(linkedin_poster_module)

        # Initialize the poster with default vault path
        poster = linkedin_poster_module.LinkedInPoster(vault_path="AI_Employee_Vault")

        # Create the draft for approval
        approval_file_path = poster.create_post_draft(
            content=content,
            hashtags=hashtags,
            post_type=post_type
        )

        # Extract the post ID from the file path
        post_id = Path(approval_file_path).stem

        return {
            "success": True,
            "post_id": post_id,
            "message": f"Created LinkedIn post draft: {post_id}"
        }
    except Exception as e:
        print(f"Error in create_linkedin_post_draft: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "post_id": "",
            "message": f"Error creating LinkedIn post draft: {str(e)}"
        }


def approve_linkedin_post_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for approving a LinkedIn post"""
    post_id = request.get("post_id")
    if not post_id:
        return {
            "success": False,
            "post_id": "",
            "message": "post_id is required"
        }

    try:
        vault_path = Path("AI_Employee_Vault")  # Default path
        pending_path = vault_path / "Pending_Approval"
        approved_path = vault_path / "Approved"
        approved_path.mkdir(parents=True, exist_ok=True)

        post_file = pending_path / f"{post_id}.md"
        if post_file.exists():
            # Move the post file to Approved folder
            destination = approved_path / post_file.name
            post_file.rename(destination)

            return {
                "success": True,
                "post_id": post_id,
                "message": f"LinkedIn post {post_id} approved and moved to Approved folder"
            }
        else:
            return {
                "success": False,
                "post_id": post_id,
                "message": f"LinkedIn post {post_id} not found in pending approval"
            }

    except Exception as e:
        return {
            "success": False,
            "post_id": "",
            "message": f"Error approving LinkedIn post: {str(e)}"
        }


class LinkedInPosterMCP:
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.fastmcp = FastMCP("LinkedIn Poster MCP Server")

        # Register tools with FastMCP

        # Create tool instances with proper parameters
        create_draft_tool = Tool(
            name="create_linkedin_post_draft",
            description="Create a LinkedIn post draft that requires human approval",
            parameters=LinkedInPostRequest.model_json_schema()
        )

        approve_post_tool = Tool(
            name="approve_linkedin_post",
            description="Move a LinkedIn post from pending approval to approved status",
            parameters={
                "type": "object",
                "properties": {
                    "post_id": {"type": "string", "description": "The ID of the post to approve"}
                },
                "required": ["post_id"]
            }
        )

        # Add tools to the FastMCP instance
        self.fastmcp.add_tool(create_draft_tool)
        self.fastmcp.add_tool(approve_post_tool)

    async def create_linkedin_post_draft(self, request: LinkedInPostRequest) -> LinkedInPostResponse:
        """Create a LinkedIn post draft in the vault for approval"""
        try:

            # Import the LinkedInPoster class from the skills directory
            spec = importlib.util.spec_from_file_location(
                "linkedin_poster_impl",
                "E:\\Hackathon 0\\Bronze\\Personal-AI-Employee\\.claude\\skills\\linkedin_poster_impl.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Failed to load module spec for linkedin_poster_impl")
            linkedin_poster_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(linkedin_poster_module)

            # Initialize the poster with the vault path
            poster = linkedin_poster_module.LinkedInPoster(vault_path=str(self.vault_path))

            # Create the draft for approval
            approval_file_path = poster.create_post_draft(
                content=request.content,
                hashtags=request.hashtags,
                post_type=request.post_type
            )

            # Extract the post ID from the file path
            post_id = Path(approval_file_path).stem

            return LinkedInPostResponse(
                success=True,
                post_id=post_id,
                message=f"Created LinkedIn post draft: {post_id}"
            )
        except Exception as e:
            print(f"Error in create_linkedin_post_draft: {e}")

            traceback.print_exc()
            return LinkedInPostResponse(
                success=False,
                post_id="",
                message=f"Error creating LinkedIn post draft: {str(e)}"
            )

    async def approve_linkedin_post(self, request: Dict[str, str]) -> LinkedInPostResponse:
        """Move a LinkedIn post from pending approval to approved"""
        try:
            post_id = request.get("post_id")
            if not post_id:
                return LinkedInPostResponse(
                    success=False,
                    post_id="",
                    message="post_id is required"
                )

            pending_path = self.vault_path / "Pending_Approval"
            approved_path = self.vault_path / "Approved"
            approved_path.mkdir(parents=True, exist_ok=True)

            post_file = pending_path / f"{post_id}.md"
            if post_file.exists():
                # Move the post file to Approved folder
                destination = approved_path / post_file.name
                post_file.rename(destination)

                return LinkedInPostResponse(
                    success=True,
                    post_id=post_id,
                    message=f"LinkedIn post {post_id} approved and moved to Approved folder"
                )
            else:
                return LinkedInPostResponse(
                    success=False,
                    post_id=post_id,
                    message=f"LinkedIn post {post_id} not found in pending approval"
                )

        except Exception as e:
            return LinkedInPostResponse(
                success=False,
                post_id="",
                message=f"Error approving LinkedIn post: {str(e)}"
            )

    def serve(self, host: str = "localhost", port: int = 8001):
        """Start the MCP server"""
        return self.fastmcp.run(transport="stdio", show_banner=False)


def main():

    parser = argparse.ArgumentParser(description="LinkedIn Poster MCP Server")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")

    args = parser.parse_args()

    server = LinkedInPosterMCP(vault_path=args.vault_path)

    print(f"Starting LinkedIn Poster MCP Server on {args.host}:{args.port}")
    print(f"Vault path: {args.vault_path}")

    server.serve(host=args.host, port=args.port)


if __name__ == "__main__":
    main()