"""
CEO Briefing Generator - Data Aggregation Module

This module handles the aggregation of data from multiple sources for the CEO briefing:
- Business_Goals.md for strategic objectives
- Odoo accounting system for revenue data
- Social media summaries for engagement metrics
- System logs for process analysis
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml

class CEOSummaryAggregator:
    """Aggregates data from multiple business sources for CEO briefings."""

    def __init__(self):
        # Get the project root directory (where the main files are)
        import __main__
        import inspect
        import sys

        # Determine the project root based on the main script location
        if hasattr(__main__, '__file__'):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__main__.__file__)))
        else:
            # Fallback: assume we're running from the project root
            project_root = os.getcwd()
            if 'watcher' in project_root:
                project_root = os.path.dirname(project_root)  # Go up one level from watcher/

        self.vault_path = os.path.join(project_root, "AI_Employee_Vault")
        self.briefings_path = os.path.join(self.vault_path, "Briefings")
        self.logs_path = os.path.join(self.vault_path, "Logs")
        self.accounting_path = os.path.join(self.vault_path, "Accounting")

    def aggregate_briefing_data(self) -> Dict:
        """
        Aggregate all data sources for the CEO briefing.

        Returns:
            Dictionary containing all briefing data organized by section
        """
        briefing_data = {
            'revenue_data': self._get_revenue_data(),
            'business_goals': self._get_business_goals_data(),
            'bottlenecks': self._get_bottleneck_data(),
            'suggestions': self._get_suggestions(),
            'upcoming_deadlines': self._get_upcoming_deadlines(),
            'social_metrics': self._get_social_metrics(),
            'system_logs_analysis': self._get_system_logs_analysis()
        }

        return briefing_data

    def _get_revenue_data(self) -> Dict:
        """Extract revenue data from Odoo accounting system."""
        # This would normally connect to Odoo via MCP
        # For now, we'll mock the data or look for any existing accounting files
        try:
            # Try to find Odoo data files if they exist
            revenue_data = {
                'current_week_revenue': 0,
                'previous_week_revenue': 0,
                'budget_target': 0,
                'revenue_categories': {}
            }

            # Look for potential accounting data in the Accounting directory
            if os.path.exists(self.accounting_path):
                for file_name in os.listdir(self.accounting_path):
                    if file_name.endswith('.json') or file_name.endswith('.csv'):
                        # This is where we'd process actual accounting data
                        # For now, we'll return placeholder data
                        revenue_data['current_week_revenue'] = 45000  # Placeholder
                        revenue_data['previous_week_revenue'] = 42000  # Placeholder
                        revenue_data['budget_target'] = 50000  # Placeholder
                        revenue_data['revenue_categories'] = {
                            'Services': 30000,
                            'Products': 15000
                        }
                        break

            return revenue_data
        except Exception as e:
            print(f"Error retrieving revenue data: {str(e)}")
            return {
                'current_week_revenue': 0,
                'previous_week_revenue': 0,
                'budget_target': 0,
                'revenue_categories': {},
                'error': str(e)
            }

    def _get_business_goals_data(self) -> Dict:
        """Extract business goals and progress from Business_Goals.md."""
        try:
            goals_file_path = os.path.join(self.vault_path, "Business_Goals.md")
            if not os.path.exists(goals_file_path):
                return {
                    'goals': [],
                    'error': 'Business_Goals.md not found'
                }

            with open(goals_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple parsing to extract goals - this could be more sophisticated
            goals = []

            # Find sections that look like goals
            # This is a basic pattern - could be enhanced based on actual file structure
            goal_patterns = [
                r'##\s*Goal.*?\n(.*?)(?=\n##\s|\Z)',  # Goals defined with ## headers
                r'-\s*\[.\]\s*(Goal.*?)(?=\n-\s*\[)',  # Goals as checklist items
            ]

            for pattern in goal_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    goals.append(match.strip())

            # If no structured goals found, try to identify any goal-related content
            if not goals:
                # Look for common goal indicators
                content_lower = content.lower()
                if 'goal' in content_lower or 'objective' in content_lower or 'target' in content_lower:
                    # Extract paragraphs that might contain goals
                    paragraphs = content.split('\n\n')
                    for para in paragraphs:
                        if any(indicator in para.lower() for indicator in ['goal', 'objective', 'target', 'aim']):
                            goals.append(para.strip())

            return {
                'goals': goals,
                'total_goals': len(goals)
            }
        except Exception as e:
            print(f"Error retrieving business goals data: {str(e)}")
            return {
                'goals': [],
                'error': str(e)
            }

    def _get_bottleneck_data(self) -> List[str]:
        """Identify potential bottlenecks by analyzing system logs."""
        try:
            bottlenecks = []

            # Look for recent log files
            if not os.path.exists(self.logs_path):
                return ['No system logs found for bottleneck analysis']

            # Get the most recent log files (last week)
            one_week_ago = datetime.now() - timedelta(days=7)

            for file_name in os.listdir(self.logs_path):
                if file_name.endswith('.md'):
                    file_path = os.path.join(self.logs_path, file_name)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_date >= one_week_ago:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Look for error patterns that indicate bottlenecks
                        error_patterns = [
                            r'error',
                            r'failed',
                            r'timeout',
                            r'unavailable',
                            r'blocked',
                            r'delay'
                        ]

                        for pattern in error_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                bottlenecks.append(f"Potential bottleneck identified in {file_name}: {pattern}")

            # If we couldn't find specific bottlenecks, return a default message
            if not bottlenecks:
                bottlenecks = ['No specific bottlenecks identified in recent logs']

            return bottlenecks[:5]  # Limit to top 5 bottlenecks
        except Exception as e:
            print(f"Error analyzing system logs for bottlenecks: {str(e)}")
            return [f"Error during bottleneck analysis: {str(e)}"]

    def _get_suggestions(self) -> List[str]:
        """Generate proactive business suggestions based on available data."""
        try:
            suggestions = []

            # Get current date to determine week
            current_date = datetime.now()

            # Generic suggestions based on common business practices
            suggestions.extend([
                "Review resource allocation for high-priority projects",
                "Consider expanding high-performing service categories",
                "Optimize processes that have shown recent delays",
                "Follow up on pending approvals that may be blocking progress",
                f"Scheduled weekly review for week of {current_date.strftime('%Y-%m-%d')}"
            ])

            return suggestions
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            return [f"Error during suggestions generation: {str(e)}"]

    def _get_upcoming_deadlines(self) -> List[Dict]:
        """Identify upcoming deadlines from business goals and logs."""
        try:
            deadlines = []

            # Look in business goals for deadlines
            goals_data = self._get_business_goals_data()
            if goals_data.get('goals'):
                # This would look for dates in goal descriptions
                for goal in goals_data['goals'][:3]:  # Just look at first 3 goals
                    # Look for date patterns
                    date_pattern = r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b'  # YYYY-MM-DD
                    matches = re.findall(date_pattern, goal)

                    for match in matches:
                        year, month, day = match
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        try:
                            deadline_date = datetime.strptime(date_str, "%Y-%m-%d")
                            if deadline_date > datetime.now():
                                deadlines.append({
                                    'date': date_str,
                                    'description': goal[:100],  # First 100 chars
                                    'priority': 'Medium'
                                })
                        except:
                            continue

            # If we didn't find deadlines in goals, add some generic ones
            if not deadlines:
                next_week = datetime.now() + timedelta(weeks=1)
                deadlines = [
                    {
                        'date': next_week.strftime('%Y-%m-%d'),
                        'description': 'Weekly business review meeting',
                        'priority': 'High'
                    },
                    {
                        'date': (next_week + timedelta(days=3)).strftime('%Y-%m-%d'),
                        'description': 'Monthly financial report deadline',
                        'priority': 'High'
                    }
                ]

            # Sort by date
            deadlines.sort(key=lambda x: x['date'])

            return deadlines[:5]  # Limit to top 5 deadlines
        except Exception as e:
            print(f"Error identifying upcoming deadlines: {str(e)}")
            return [{
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': f'Error identifying deadlines: {str(e)}',
                'priority': 'Low'
            }]

    def _get_social_metrics(self) -> Dict:
        """Get social media engagement metrics."""
        try:
            # Placeholder for actual social metrics
            # This would normally connect to LinkedIn MCP
            return {
                'linkedin_engagement': 'Data not available (requires LinkedIn MCP connection)',
                'recent_posts_count': 0,
                'average_engagement_rate': '0%'
            }
        except Exception as e:
            print(f"Error retrieving social metrics: {str(e)}")
            return {
                'error': str(e),
                'linkedin_engagement': 'Unavailable',
            }

    def _get_system_logs_analysis(self) -> Dict:
        """Analyze system logs for performance and health indicators."""
        try:
            log_stats = {
                'processed_files': 0,
                'errors_count': 0,
                'warnings_count': 0,
                'recent_activities': []
            }

            if not os.path.exists(self.logs_path):
                return log_stats

            # Analyze recent log files
            for file_name in os.listdir(self.logs_path):
                if file_name.endswith('.md'):
                    file_path = os.path.join(self.logs_path, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    log_stats['processed_files'] += 1
                    log_stats['errors_count'] += len(re.findall(r'error|failed', content, re.IGNORECASE))
                    log_stats['warnings_count'] += len(re.findall(r'warning|caution', content, re.IGNORECASE))

                    # Get recent activities (last few log entries)
                    lines = content.split('\n')
                    for line in lines[-5:]:  # Last 5 lines
                        if line.strip() and not line.startswith('#'):
                            log_stats['recent_activities'].append(line.strip())

            # Limit recent activities to avoid too much data
            log_stats['recent_activities'] = log_stats['recent_activities'][-10:]

            return log_stats
        except Exception as e:
            print(f"Error analyzing system logs: {str(e)}")
            return {
                'error': str(e),
                'processed_files': 0,
                'errors_count': 0,
                'warnings_count': 0,
                'recent_activities': []
            }


def generate_briefing_report() -> str:
    """
    Generate the complete CEO briefing report as a Markdown string.

    Returns:
        Formatted Markdown string of the CEO briefing
    """
    aggregator = CEOSummaryAggregator()
    data = aggregator.aggregate_briefing_data()

    # Generate the report
    report_lines = [
        f"# Weekly CEO Briefing - Week of {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Revenue This Week",
        ""
    ]

    revenue = data.get('revenue_data', {})
    if revenue.get('error'):
        report_lines.append(f"- **Revenue data unavailable**: {revenue['error']}")
    else:
        current_revenue = revenue.get('current_week_revenue', 0)
        prev_revenue = revenue.get('previous_week_revenue', 0)
        budget_target = revenue.get('budget_target', 0)

        report_lines.append(f"- Total revenue: ${current_revenue:,}")

        if prev_revenue > 0:
            change = ((current_revenue - prev_revenue) / prev_revenue) * 100
            direction = "increase" if change >= 0 else "decrease"
            report_lines.append(f"- Comparison to previous week: {change:+.1f}% {direction}")

        if budget_target > 0:
            progress = (current_revenue / budget_target) * 100
            report_lines.append(f"- Progress toward budget target: {progress:.1f}%")

        categories = revenue.get('revenue_categories', {})
        if categories:
            report_lines.append("- Revenue by category:")
            for category, amount in categories.items():
                report_lines.append(f"  - {category}: ${amount:,}")

    report_lines.extend([
        "",
        "## Current Bottlenecks",
        ""
    ])

    bottlenecks = data.get('bottlenecks', [])
    if bottlenecks:
        for bottleneck in bottlenecks:
            report_lines.append(f"- {bottleneck}")
    else:
        report_lines.append("- No significant bottlenecks identified")

    report_lines.extend([
        "",
        "## Proactive Suggestions",
        ""
    ])

    suggestions = data.get('suggestions', [])
    if suggestions:
        for suggestion in suggestions:
            report_lines.append(f"- {suggestion}")
    else:
        report_lines.append("- No specific suggestions at this time")

    report_lines.extend([
        "",
        "## Upcoming Deadlines",
        ""
    ])

    deadlines = data.get('upcoming_deadlines', [])
    if deadlines:
        for deadline in deadlines:
            priority = deadline.get('priority', 'Medium')
            report_lines.append(f"- **{priority}** {deadline['date']}: {deadline['description']}")
    else:
        report_lines.append("- No upcoming deadlines identified")

    # Add business goals summary if available
    goals = data.get('business_goals', {}).get('goals', [])
    if goals:
        report_lines.extend([
            "",
            "## Business Goals Update",
            ""
        ])
        for i, goal in enumerate(goals[:3]):  # Show first 3 goals
            report_lines.append(f"- {goal[:100]}{'...' if len(goal) > 100 else ''}")

    # Add system logs summary
    log_analysis = data.get('system_logs_analysis', {})
    report_lines.extend([
        "",
        "## System Health",
        f"- Processed files: {log_analysis.get('processed_files', 0)}",
        f"- Errors detected: {log_analysis.get('errors_count', 0)}",
        f"- Warnings issued: {log_analysis.get('warnings_count', 0)}"
    ])

    if log_analysis.get('recent_activities'):
        report_lines.append("")
        report_lines.append("Recent system activities:")
        for activity in log_analysis['recent_activities'][:5]:  # Limit to 5
            report_lines.append(f"- {activity}")

    return "\n".join(report_lines)


def save_briefing_to_file(report_content: str, filename: Optional[str] = None) -> str:
    """
    Save the briefing report to a file in the Briefings directory.

    Args:
        report_content: The Markdown content of the briefing
        filename: Optional filename, defaults to weekly_briefing_YYYY-MM-DD.md

    Returns:
        Path to the saved file
    """
    # Determine project root
    import __main__
    import sys

    if hasattr(__main__, '__file__'):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__main__.__file__)))
    else:
        # Fallback: assume we're running from the project root
        project_root = os.getcwd()
        if 'watcher' in project_root:
            project_root = os.path.dirname(project_root)  # Go up one level from watcher/

    vault_path = os.path.join(project_root, "AI_Employee_Vault")
    briefings_path = os.path.join(vault_path, "Briefings")

    if not os.path.exists(briefings_path):
        os.makedirs(briefings_path)

    if filename is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"weekly_briefing_{date_str}.md"

    file_path = os.path.join(briefings_path, filename)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return file_path


if __name__ == "__main__":
    # Generate and save a sample briefing
    report = generate_briefing_report()
    file_path = save_briefing_to_file(report)
    print(f"CEO Briefing generated and saved to: {file_path}")