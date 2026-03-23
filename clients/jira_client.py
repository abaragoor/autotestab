"""JIRA Cloud REST API client."""
import requests
from requests.auth import HTTPBasicAuth
import config

class JiraClient:
    def __init__(self):
        self.base = f"{config.JIRA_URL}/rest/api/3"
        self.auth = HTTPBasicAuth(config.JIRA_USER, config.JIRA_API_KEY)
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def create_bug(self, summary: str, description: str, priority: str = "Medium") -> dict:
        payload = {
            "fields": {
                "project": {"key": config.JIRA_PROJECT_KEY},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
                },
                "issuetype": {"name": "Bug"},
                "priority": {"name": priority},
            }
        }
        r = requests.post(
            f"{self.base}/issue",
            json=payload, auth=self.auth, headers=self.headers
        )
        r.raise_for_status()
        return r.json()
