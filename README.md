# NextGen AI Test Automation — MacBook Air Setup Guide
**V1 Demo: Roku Screensaver Feature**
Skipping: Jenkins, GitHub automation

---

## What you'll have running in ~30 minutes

Story text → Claude → TestRail test cases → Claude-generated pytest → Roku ECP → HTML report → JIRA bug recommendations

---

## Step 1: One-time installs

Open Terminal and run these in order.

### 1a. Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
After install, follow the "Next steps" it prints (adds brew to PATH).

### 1b. Python 3.11
```bash
brew install python@3.11
python3 --version   # should show 3.11.x
```

### 1c. Node.js (needed for Claude Code CLI)
```bash
brew install node
node --version   # should show v20+
```

### 1d. Claude Code CLI
```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

---

## Step 2: Create your project

```bash
mkdir ~/roku-ai-test
cd ~/roku-ai-test

# Create a virtual environment (keeps dependencies clean)
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install anthropic fastmcp pytest pytest-html requests python-dotenv
```

---

## Step 3: Project structure

Create this exact folder structure:

```
roku-ai-test/
├── .env                    ← your API keys (never commit this)
├── config.py               ← loads env vars
├── pipeline.py             ← main demo runner (run this)
├── clients/
│   ├── __init__.py
│   ├── testrail.py         ← TestRail REST client
│   ├── jira_client.py      ← JIRA REST client
│   └── roku_ecp.py         ← Roku ECP client
├── tests/                  ← Claude writes pytest files here
│   └── __init__.py
└── reports/                ← HTML reports land here
```

```bash
mkdir -p clients tests reports
touch clients/__init__.py tests/__init__.py
```

---

## Step 4: Configure your API keys

Create `.env` in your project root:

```bash
cat > .env << 'EOF'
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# TestRail
TESTRAIL_URL=https://yourcompany.testrail.io
TESTRAIL_USER=your@email.com
TESTRAIL_API_KEY=your_testrail_api_key
TESTRAIL_PROJECT_ID=1

# JIRA
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USER=your@email.com
JIRA_API_KEY=your_jira_api_key
JIRA_PROJECT_KEY=ROKU

# Roku (find Roku IP: Settings > Network > About on the Roku)
ROKU_IP=192.168.1.xxx
EOF
```

> **Finding your Roku IP**: On the Roku, go to Settings → Network → About. The IP address is listed there.
> **Roku developer mode**: Settings → System → Advanced system settings → Developer mode → Enable

---

## Step 5: The code files

Get it from this GitHub repo

---


## Step 6: Run the demo

```bash
# Make sure venv is active
source venv/bin/activate

# First, do a dry run to validate setup (no API calls)
python pipeline.py --dry-run   (Gets the user story from user_story.txt)

# Full run with the screensaver demo story
python pipeline.py

# Or with a custom story
python pipeline.py --story "The Roku device allows users to connect a Google Photos album as a screensaver source."

# Open the HTML report
open reports/report_*.html
```

---

## Step 7: Use Claude Code for interactive development

Claude Code lets you iterate on the generated tests conversationally:

```bash
# In your project directory
claude

# Then ask things like:
# "Add a test case for when the screensaver timeout is set to the maximum value"
# "The Roku ECP navigation to screensaver settings is failing — fix the key sequence"
# "Generate a conftest.py with shared fixtures for all Roku tests"
```

---

## Troubleshooting

### Roku not reachable
- Confirm both your Mac and Roku are on the same WiFi network
- On Roku: Settings → Network → About → IP address
- Enable developer mode: Settings → System → Advanced system settings → Developer mode
- Try: `curl http://ROKU_IP:8060/query/device-info`

### TestRail 401 error
- Use your API key, not your password (generate at: Account Settings → API Keys)
- URL should NOT have a trailing slash

### JIRA 401 error  
- Use an API token: id.atlassian.com → Security → API tokens
- The user field should be your email address

### Claude API errors
- Confirm `ANTHROPIC_API_KEY` starts with `sk-ant-`
- Check your usage limits at console.anthropic.com

---

## What's skipped for now (V2/V3)

- **Jenkins**: V1 uses `python pipeline.py` locally — Jenkins adds CI trigger in V2
- **GitHub PR automation**: V2 adds `gh pr create` after codegen
- **Auto JIRA filing**: V1 shows recommendations; V2 auto-files with deduplication
- **Retry/flaky classification**: V2 adds `pytest-rerunfailures`
- **Multilingual stories**: V1 handles English; V3 adds translation layer

---

## Demo script for the presentation

1. Show the story text (slide 9 — screensaver feature)
2. Run: `python pipeline.py --dry-run` → shows the pipeline without waiting
3. Run: `python pipeline.py` → live with real Roku
4. Open TestRail → show the test cases that were created
5. Open `reports/report_*.html` → show pass/fail
6. Show JIRA bug recommendations in terminal

Total demo time: ~3-5 minutes once Roku is connected.
