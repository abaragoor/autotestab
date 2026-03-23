import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")
TESTRAIL_URL        = os.getenv("TESTRAIL_URL")
TESTRAIL_USER       = os.getenv("TESTRAIL_USER")
TESTRAIL_API_KEY    = os.getenv("TESTRAIL_API_KEY")
TESTRAIL_PROJECT_ID = int(os.getenv("TESTRAIL_PROJECT_ID", "2"))
JIRA_URL            = os.getenv("JIRA_URL")
JIRA_USER           = os.getenv("JIRA_USER")
JIRA_API_KEY        = os.getenv("JIRA_API_KEY")
JIRA_PROJECT_KEY    = os.getenv("JIRA_PROJECT_KEY", "ROKU")
ROKU_IP             = os.getenv("ROKU_IP", "10.0.0.110")
