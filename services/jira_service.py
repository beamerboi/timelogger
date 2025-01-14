import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from jira import JIRA
from jira.exceptions import JIRAError
from flask import current_app
from config.config import Config
from datetime import datetime

class JiraService:
    def __init__(self):
        print("\n" + "=" * 80)
        print("JIRA SERVICE INITIALIZATION STARTED")
        print("=" * 80)
        print(f"Time: {datetime.now()}")
        print(f"Server URL: {Config.JIRA_SERVER}")
        print(f"Auth Email: {Config.JIRA_EMAIL}")

        try:
            print("\nCreating JIRA client...")
            self.jira = JIRA(
                options={
                    'server': Config.JIRA_SERVER,
                    'verify': False
                },
                basic_auth=(Config.JIRA_EMAIL, Config.JIRA_API_TOKEN)
            )
            print("✓ JIRA client created successfully")
        except Exception as e:
            import traceback
            print("\nERROR CREATING JIRA CLIENT:")
            print(traceback.format_exc())
            self.jira = None

        print("=" * 80)

    def get_current_sprint_tickets(self, user_email):
        """Get tickets for the specified user (not necessarily the auth user)"""
        print("\n=== GETTING TICKETS ===")
        print(f"Fetching tickets for user: {user_email}")

        if not self.jira:
            print("✗ No JIRA client available")
            return []

        try:
            # Using your JQL pattern
            jql = (
                f'assignee = "{user_email}" AND '
                'status = "In Progress" AND '
                'sprint IN openSprints()'
            )

            print(f"\nExecuting JQL: {jql}")
            issues = self.jira.search_issues(
                jql,
                fields=['key', 'summary', 'status', 'project'],
                maxResults=50
            )

            print(f"\nFound {len(issues)} issues:")
            for issue in issues:
                print(f"- {issue.key}: {issue.fields.summary} "
                      f"({issue.fields.status.name}) "
                      f"[{issue.fields.project.key}]")

            return issues

        except JIRAError as e:
            print(f"✗ JIRA Search Error: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return []
        except Exception as e:
            print(f"✗ Unexpected error during search: {str(e)}")
            return []

    def test_connection(self):
        print("\n=== TESTING JIRA CONNECTION ===")
        if not self.jira:
            print("✗ No JIRA client available")
            return False

        try:
            print("Getting current user info...")
            myself = self.jira.myself()
            print(f"✓ Connected as: {myself.get('displayName')} ({myself.get('emailAddress')})")

            print("\nGetting projects...")
            projects = self.jira.projects()
            print(f"✓ Found {len(projects)} accessible projects:")
            for project in projects:
                print(f"- {project.key}: {project.name}")

            return True
        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            return False

    def log_work(self, ticket_id, time_spent, comment):
        if not self.jira:
            return False

        try:
            self.jira.add_worklog(
                issue=ticket_id,
                timeSpent=f"{time_spent}h",
                comment=comment
            )
            return True
        except JIRAError as e:
            print(f"Failed to log work: {str(e)}")
            return False