"""TestRail REST API client (v2)."""
import requests
from requests.auth import HTTPBasicAuth
import config

class TestRailClient:
    def __init__(self):
        self.base = f"{config.TESTRAIL_URL}/index.php?/api/v2"
        self.auth = HTTPBasicAuth(config.TESTRAIL_USER, config.TESTRAIL_API_KEY)
        self.headers = {"Content-Type": "application/json"}

    def create_suite(self, project_id: int, name: str, description: str = "") -> dict:
        payload = {"name": name, "description": description}
        r = requests.post(
            f"{self.base}/add_suite/{project_id}",
            json=payload, auth=self.auth, headers=self.headers
        )
        r.raise_for_status()
        return r.json()

    def create_section(self, project_id: int, suite_id: int, name: str) -> dict:
        payload = {"name": name, "suite_id": suite_id}
        r = requests.post(
            f"{self.base}/add_section/{project_id}",
            json=payload, auth=self.auth, headers=self.headers
        )
        r.raise_for_status()
        return r.json()

    def add_case(self, section_id: int, title: str, steps: str, expected: str) -> dict:
        payload = {
            "title": title,
            "type_id": 1,           # Automated
            "priority_id": 2,       # Medium
            "custom_steps": steps,
            "custom_expected": expected,
        }
        r = requests.post(
            f"{self.base}/add_case/{section_id}",
            json=payload, auth=self.auth, headers=self.headers
        )
        r.raise_for_status()
        return r.json()

    def create_run(self, project_id: int, suite_id: int, name: str, case_ids: list) -> dict:
        payload = {
            "name": name,
            "suite_id": suite_id,
            "case_ids": case_ids,
            "include_all": False,
        }
        r = requests.post(
            f"{self.base}/add_run/{project_id}",
            json=payload, auth=self.auth, headers=self.headers
        )
        r.raise_for_status()
        return r.json()
