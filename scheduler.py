"""
Scheduling System for Personal AI Employee
Manages periodic execution of tasks like email checking, LinkedIn posting, etc.
"""
import os
import time
import threading
import schedule
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Any, List
import importlib.util
import subprocess
import sys


class TaskScheduler:
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.scheduled_jobs = []
        self.running = False
        self.scheduler_thread = None

    def schedule_email_checking(self, interval_minutes: int = 5):
        """Schedule periodic email checking"""
        def run_email_check():
            try:
                print(f"[{datetime.now()}] Running scheduled email check...")

                # Import the GmailWatcher from the skills directory
                spec = importlib.util.spec_from_file_location(
                    "gmail_watcher_impl",
                    "E:\\Hackathon 0\\Bronze\\Personal-AI-Employee\\.claude\\skills\\gmail_watcher_impl.py"
                )
                gmail_watcher_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(gmail_watcher_module)

                # Create a simple GmailWatcher instance to check emails
                watcher = gmail_watcher_module.GmailWatcher(
                    credentials_path=os.getenv("GMAIL_CREDENTIALS_PATH", ""),
                    vault_path=str(self.vault_path)
                )

                # Run the check_emails method with default parameters
                # This would typically check for new emails and create files in the vault
                watcher.check_emails(max_emails=10, unread_only=True)
                print("Email check completed")
            except Exception as e:
                print(f"Error during scheduled email check: {e}")
                import traceback
                traceback.print_exc()

        # Schedule the job
        job = schedule.every(interval_minutes).minutes.do(run_email_check)
        self.scheduled_jobs.append(job)
        print(f"Scheduled email checking every {interval_minutes} minutes")

    def schedule_linkedin_post_check(self, interval_minutes: int = 10):
        """Schedule periodic checking for approved LinkedIn posts"""
        def run_linkedin_check():
            try:
                print(f"[{datetime.now()}] Running scheduled LinkedIn post check...")

                # Import the LinkedIn poster implementation
                spec = importlib.util.spec_from_file_location(
                    "linkedin_poster_impl",
                    ".claude.skills.linkedin_poster_impl.py"
                )
                linkedin_poster_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(linkedin_poster_module)

                # Look for approved LinkedIn posts in the vault
                approved_path = self.vault_path / "Approved"
                if approved_path.exists():
                    approved_files = list(approved_path.glob("LINKEDIN_POST_*.md"))

                    for post_file in approved_files:
                        print(f"Found approved LinkedIn post: {post_file.name}")

                        # Initialize the poster and process the file
                        poster = linkedin_poster_module.LinkedInPoster(vault_path=str(self.vault_path))
                        poster.process_approval_file(str(post_file))

                        # Close any browser instances if they were opened
                        if hasattr(poster, 'close'):
                            poster.close()

                print("LinkedIn post check completed")
            except Exception as e:
                print(f"Error during scheduled LinkedIn post check: {e}")
                import traceback
                traceback.print_exc()

        # Schedule the job
        job = schedule.every(interval_minutes).minutes.do(run_linkedin_check)
        self.scheduled_jobs.append(job)
        print(f"Scheduled LinkedIn post check every {interval_minutes} minutes")

    def schedule_approval_workflow(self, interval_minutes: int = 2):
        """Schedule periodic approval workflow checks"""
        def run_approval_check():
            try:
                print(f"[{datetime.now()}] Running scheduled approval workflow check...")

                # Import and run the approval workflow
                spec = importlib.util.spec_from_file_location(
                    "approval_workflow",
                    "approval_workflow.py"
                )
                approval_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(approval_module)

                workflow = approval_module.ApprovalWorkflow(vault_path=str(self.vault_path))
                workflow.process_pending_approvals()

                print("Approval workflow check completed")
            except Exception as e:
                print(f"Error during scheduled approval workflow check: {e}")
                import traceback
                traceback.print_exc()

        # Schedule the job
        job = schedule.every(interval_minutes).minutes.do(run_approval_check)
        self.scheduled_jobs.append(job)
        print(f"Scheduled approval workflow check every {interval_minutes} minutes")

    def schedule_ceo_briefing(self):
        """Schedule the CEO briefing generation for Sunday nights at 11:59 PM"""
        def run_briefing_generation():
            try:
                print(f"[{datetime.now()}] Running scheduled CEO briefing generation...")

                # Import and run the CEO briefing generator
                spec = importlib.util.spec_from_file_location(
                    "ceo_briefing_formatter",
                    "watcher/ceo_briefing_formatter.py"
                )
                briefing_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(briefing_module)

                # Run the main function to generate the briefing
                result = briefing_module.main()
                print(f"CEO briefing generation completed: {result}")
            except Exception as e:
                print(f"Error during scheduled CEO briefing generation: {e}")
                import traceback
                traceback.print_exc()

        # Schedule for Sunday at 23:59 (11:59 PM)
        job = schedule.every().sunday.at("23:59").do(run_briefing_generation)
        self.scheduled_jobs.append(job)
        print("Scheduled CEO briefing generation for Sunday at 11:59 PM")

    def add_custom_schedule(self, job_func: Callable, schedule_config: Dict[str, Any]):
        """
        Add a custom scheduled job

        Args:
            job_func: The function to schedule
            schedule_config: Configuration like {"minutes": 5} or {"hour": 9}
        """
        job = schedule
        for unit, value in schedule_config.items():
            if unit == "seconds":
                job = job.every(value).seconds
            elif unit == "minutes":
                job = job.every(value).minutes
            elif unit == "hours":
                job = job.every(value).hours
            elif unit == "days":
                job = job.every(value).days
            elif unit == "hour_at":
                # Schedule at a specific minute of each hour
                job = job.every().hour.at(f":{value:02d}")
            elif unit == "day_at":
                # Schedule at a specific time of each day
                job = job.every().day.at(value)

        job = job.do(job_func)
        self.scheduled_jobs.append(job)
        print(f"Added custom scheduled job with config: {schedule_config}")

    def run_pending(self):
        """Run all pending scheduled jobs"""
        schedule.run_pending()

    def start(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            print("Scheduler is already running")
            return

        self.running = True

        def run_scheduler():
            print("Scheduler started...")
            while self.running:
                schedule.run_pending()
                time.sleep(1)

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("Scheduler thread started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        print("Scheduler stopped")

    def list_jobs(self):
        """List all scheduled jobs"""
        print(f"Currently scheduled jobs: {len(self.scheduled_jobs)}")
        for i, job in enumerate(self.scheduled_jobs, 1):
            print(f"  {i}. {job}")


class SchedulerCLI:
    """Command-line interface for the scheduler"""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.scheduler = TaskScheduler(vault_path)

    def setup_default_schedule(self):
        """Set up the default schedule for the Personal AI Employee"""
        print("Setting up default schedule...")

        # Schedule email checking every 5 minutes
        self.scheduler.schedule_email_checking(interval_minutes=5)

        # Schedule LinkedIn post checking every 10 minutes
        self.scheduler.schedule_linkedin_post_check(interval_minutes=10)

        # Schedule approval workflow checking every 2 minutes
        self.scheduler.schedule_approval_workflow(interval_minutes=2)

        # Schedule CEO briefing generation for Sunday nights
        self.scheduler.schedule_ceo_briefing()

        print("Default schedule set up successfully")

    def run_once(self):
        """Run scheduled tasks once"""
        print("Running scheduled tasks once...")
        schedule.run_all()
        print("All scheduled tasks completed")

    def run_continuous(self):
        """Run the scheduler continuously"""
        self.scheduler.start()

        try:
            print("Scheduler running continuously. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            self.scheduler.stop()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scheduling System for Personal AI Employee")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--setup-default", action="store_true", help="Set up default schedule")
    parser.add_argument("--run-once", action="store_true", help="Run scheduled tasks once")
    parser.add_argument("--continuous", action="store_true", help="Run scheduler continuously")

    args = parser.parse_args()

    scheduler_cli = SchedulerCLI(vault_path=args.vault_path)

    if args.setup_default:
        scheduler_cli.setup_default_schedule()

    if args.run_once:
        scheduler_cli.run_once()
    elif args.continuous:
        scheduler_cli.run_continuous()
    else:
        # If no specific action, just set up the default schedule
        scheduler_cli.setup_default_schedule()
        print("Default schedule configured. Use --run-once to execute once or --continuous to run continuously.")


if __name__ == "__main__":
    main()