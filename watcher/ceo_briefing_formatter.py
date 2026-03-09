"""
CEO Briefing Generator - Formatting Module

This module handles the formatting and generation of the CEO briefing content
based on aggregated data from multiple sources.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ceo_briefing_aggregator import CEOSummaryAggregator, generate_briefing_report, save_briefing_to_file


class CEOSummaryFormatter:
    """Formats the CEO briefing from aggregated data."""

    def __init__(self):
        self.aggregator = CEOSummaryAggregator()

    def format_revenue_section(self, revenue_data: Dict) -> str:
        """
        Format the revenue section of the briefing.

        Args:
            revenue_data: Dictionary containing revenue information

        Returns:
            Formatted Markdown string for revenue section
        """
        lines = ["## Revenue This Week", ""]

        if revenue_data.get('error'):
            lines.append(f"- **Revenue data unavailable**: {revenue_data['error']}")
        else:
            current_revenue = revenue_data.get('current_week_revenue', 0)
            prev_revenue = revenue_data.get('previous_week_revenue', 0)
            budget_target = revenue_data.get('budget_target', 0)

            lines.append(f"- Total revenue: ${current_revenue:,}")

            if prev_revenue > 0:
                change = ((current_revenue - prev_revenue) / prev_revenue) * 100
                direction = "increase" if change >= 0 else "decrease"
                lines.append(f"- Comparison to previous week: {change:+.1f}% {direction}")

            if budget_target > 0:
                progress = (current_revenue / budget_target) * 100
                lines.append(f"- Progress toward budget target: {progress:.1f}%")

            categories = revenue_data.get('revenue_categories', {})
            if categories:
                lines.append("- Revenue by category:")
                for category, amount in categories.items():
                    lines.append(f"  - {category}: ${amount:,}")

        return "\n".join(lines)

    def format_bottlenecks_section(self, bottlenecks: List[str]) -> str:
        """
        Format the bottlenecks section of the briefing.

        Args:
            bottlenecks: List of identified bottlenecks

        Returns:
            Formatted Markdown string for bottlenecks section
        """
        lines = ["## Current Bottlenecks", ""]

        if bottlenecks:
            for bottleneck in bottlenecks:
                lines.append(f"- {bottleneck}")
        else:
            lines.append("- No significant bottlenecks identified")

        return "\n".join(lines)

    def format_suggestions_section(self, suggestions: List[str]) -> str:
        """
        Format the proactive suggestions section of the briefing.

        Args:
            suggestions: List of proactive suggestions

        Returns:
            Formatted Markdown string for suggestions section
        """
        lines = ["## Proactive Suggestions", ""]

        if suggestions:
            for suggestion in suggestions:
                lines.append(f"- {suggestion}")
        else:
            lines.append("- No specific suggestions at this time")

        return "\n".join(lines)

    def format_deadlines_section(self, deadlines: List[Dict]) -> str:
        """
        Format the upcoming deadlines section of the briefing.

        Args:
            deadlines: List of upcoming deadlines with details

        Returns:
            Formatted Markdown string for deadlines section
        """
        lines = ["## Upcoming Deadlines", ""]

        if deadlines:
            for deadline in deadlines:
                priority = deadline.get('priority', 'Medium')
                lines.append(f"- **{priority}** {deadline['date']}: {deadline['description']}")
        else:
            lines.append("- No upcoming deadlines identified")

        return "\n".join(lines)

    def format_business_goals_section(self, goals_data: Dict) -> str:
        """
        Format the business goals section of the briefing.

        Args:
            goals_data: Dictionary containing business goals information

        Returns:
            Formatted Markdown string for business goals section
        """
        lines = ["## Business Goals Update", ""]

        goals = goals_data.get('goals', [])
        if goals:
            for i, goal in enumerate(goals[:5]):  # Show first 5 goals
                lines.append(f"- {goal[:100]}{'...' if len(goal) > 100 else ''}")
        else:
            lines.append("- No business goals found in Business_Goals.md")

        return "\n".join(lines)

    def format_system_health_section(self, log_analysis: Dict) -> str:
        """
        Format the system health section of the briefing.

        Args:
            log_analysis: Dictionary containing system log analysis

        Returns:
            Formatted Markdown string for system health section
        """
        lines = ["## System Health", ""]

        lines.append(f"- Processed files: {log_analysis.get('processed_files', 0)}")
        lines.append(f"- Errors detected: {log_analysis.get('errors_count', 0)}")
        lines.append(f"- Warnings issued: {log_analysis.get('warnings_count', 0)}")

        if log_analysis.get('recent_activities'):
            lines.append("")
            lines.append("Recent system activities:")
            for activity in log_analysis['recent_activities'][:5]:  # Limit to 5
                lines.append(f"- {activity}")

        return "\n".join(lines)

    def generate_complete_briefing(self) -> str:
        """
        Generate the complete CEO briefing with all sections.

        Returns:
            Formatted Markdown string of the complete briefing
        """
        # Aggregate all data
        data = self.aggregator.aggregate_briefing_data()

        # Create the complete report
        report_lines = [
            f"# Weekly CEO Briefing - Week of {datetime.now().strftime('%Y-%m-%d')}",
            ""
        ]

        # Add each section
        report_lines.extend([
            self.format_revenue_section(data.get('revenue_data', {})),
            "",
            self.format_bottlenecks_section(data.get('bottlenecks', [])),
            "",
            self.format_suggestions_section(data.get('suggestions', [])),
            "",
            self.format_deadlines_section(data.get('upcoming_deadlines', [])),
            "",
            self.format_business_goals_section(data.get('business_goals', {})),
            "",
            self.format_system_health_section(data.get('system_logs_analysis', {}))
        ])

        return "\n".join(report_lines)

    def generate_and_save_briefing(self, filename: str = None) -> str:
        """
        Generate the complete briefing and save it to a file.

        Args:
            filename: Optional filename, defaults to weekly_briefing_YYYY-MM-DD.md

        Returns:
            Path to the saved file
        """
        briefing_content = self.generate_complete_briefing()
        return save_briefing_to_file(briefing_content, filename)


def generate_weekly_briefing() -> str:
    """
    High-level function to generate and save the weekly CEO briefing.

    Returns:
        Path to the generated briefing file
    """
    formatter = CEOSummaryFormatter()
    return formatter.generate_and_save_briefing()


def generate_sample_briefing() -> str:
    """
    Generate a sample briefing for testing purposes.

    Returns:
        The content of the sample briefing
    """
    # Use the existing generate_briefing_report function from aggregator
    from ceo_briefing_aggregator import generate_briefing_report
    return generate_briefing_report()


# Main execution function for scheduling
def main():
    """
    Main function to execute the CEO briefing generation process.
    Designed to be called by the orchestrator on Sunday nights.
    """
    try:
        print("Starting CEO Briefing Generation Process...")

        # Create formatter instance
        formatter = CEOSummaryFormatter()

        # Generate the briefing
        briefing_path = formatter.generate_and_save_briefing()

        print(f"CEO Briefing successfully generated and saved to: {briefing_path}")

        # Log the generation event
        log_briefing_generation(briefing_path)

        return briefing_path
    except Exception as e:
        print(f"Error during CEO briefing generation: {str(e)}")
        # In a real implementation, this would log to the system logs
        error_log_path = log_error(f"CEO Briefing Generation Error: {str(e)}")
        return f"Error occurred. See log: {error_log_path}"


def log_briefing_generation(briefing_path: str):
    """
    Log the briefing generation event to the system logs.

    Args:
        briefing_path: Path to the generated briefing file
    """
    try:
        # Create log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] | SYSTEM | CEO_BRIEFING_GENERATED | STATUS:success | file:{briefing_path}\n"

        # Determine today's log file path
        logs_dir = "AI_Employee_Vault/Logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        today_log_file = os.path.join(logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.md")

        # Append to today's log file
        with open(today_log_file, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Error logging briefing generation: {str(e)}")


def log_error(error_message: str) -> str:
    """
    Log an error message to the system logs.

    Args:
        error_message: Error message to log

    Returns:
        Path to the log file where error was recorded
    """
    try:
        # Create log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] | SYSTEM | CEO_BRIEFING_ERROR | STATUS:failed | error:{error_message}\n"

        # Determine today's log file path
        logs_dir = "AI_Employee_Vault/Logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        today_log_file = os.path.join(logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.md")

        # Append to today's log file
        with open(today_log_file, 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

        return today_log_file
    except Exception as e:
        print(f"Error logging error message: {str(e)}")
        return "error_logging_failed"


# If this script is run directly, generate a sample briefing
if __name__ == "__main__":
    main()