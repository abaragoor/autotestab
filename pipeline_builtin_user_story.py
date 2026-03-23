"""
NextGen AI Test Automation — V1 Demo Pipeline
Roku Screensaver Feature

Usage:
    python pipeline.py
    python pipeline.py --story "custom story text"
    python pipeline.py --dry-run   # skips actual API calls
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import anthropic

import config
from clients.testrail import TestRailClient
from clients.roku_ecp import RokuECP
from clients.jira_client import JiraClient

# ── Demo story (from your slide 9) ─────────────────────────────────────────
DEFAULT_STORY = """
Roku Device has a screensaver feature. The user can configure inactivity timeout
after which the configured screensaver starts running on the TV.
The minimum inactivity time is 1 minute. Zero means it is disabled.
The default is 30 minutes.
"""

client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def step1_normalize_and_generate(story: str) -> dict:
    """Claude normalizes the story and generates structured test cases."""
    print("\n[1/5] Claude: Normalizing story and generating test cases...")

    prompt = f"""You are a senior QA engineer. Given this user story, produce:
1. A normalized, precise version of the story (2-3 sentences)
2. A list of test cases in JSON format

User story:
{story}

Return ONLY valid JSON in this exact format:
{{
  "normalized_story": "...",
  "test_cases": [
    {{
      "id": "TC001",
      "title": "...",
      "category": "functional|boundary|negative",
      "priority": "high|medium|low",
      "preconditions": "...",
      "steps": ["step1", "step2", "..."],
      "expected_result": "...",
      "roku_ecp_keys": ["Home", "Up", "Select"]
    }}
  ]
}}

Generate 6-8 comprehensive test cases covering: default value, minimum value (1 min),
disabled (0), boundary values, persistence across reboot, and UI validation."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    result = json.loads(raw)
    print(f"   → Normalized story: {result['normalized_story'][:80]}...")
    print(f"   → Generated {len(result['test_cases'])} test cases")
    return result


def step2_push_to_testrail(test_data: dict, dry_run: bool = False) -> dict:
    """Push test cases to TestRail."""
    print("\n[2/5] TestRail: Creating suite and uploading test cases...")

    if dry_run:
        print("   → [DRY RUN] Skipping TestRail API call")
        return {"suite_id": 999, "section_id": 999, "case_ids": [1, 2, 3, 4, 5]}

    tr = TestRailClient()
    suite = tr.create_suite(
        config.TESTRAIL_PROJECT_ID,
        f"Roku Screensaver — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        test_data["normalized_story"]
    )
    section = tr.create_section(
        config.TESTRAIL_PROJECT_ID, suite["id"], "Screensaver Timeout"
    )

    case_ids = []
    for tc in test_data["test_cases"]:
        steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(tc["steps"]))
        case = tr.add_case(
            section["id"],
            tc["title"],
            steps_text,
            tc["expected_result"]
        )
        case_ids.append(case["id"])
        print(f"   → Created: {tc['title']}")

    return {"suite_id": suite["id"], "section_id": section["id"], "case_ids": case_ids}


def step3_generate_pytest(test_data: dict) -> str:
    """Claude generates pytest code for Roku ECP."""
    print("\n[3/5] Claude: Generating pytest code for Roku ECP...")

    test_cases_str = json.dumps(test_data["test_cases"], indent=2)

    prompt = f"""You are a Python automation engineer. Generate a pytest test file for Roku ECP.

Test cases to implement:
{test_cases_str}

Roku IP is loaded from: import config; config.ROKU_IP
Use the RokuECP class from: from clients.roku_ecp import RokuECP

Requirements:
- Use pytest fixtures for RokuECP setup
- Add a connectivity check fixture that skips if Roku is unreachable
- Use time.sleep() appropriately (Roku menus take ~1s to respond)
- Add clear docstrings for each test
- Use pytest.mark for categories: @pytest.mark.functional, @pytest.mark.boundary, @pytest.mark.negative
- Include a conftest.py section at the top as a comment showing the fixture
- Handle test failures gracefully with helpful assertion messages
- For screensaver timeout: use keypress navigation to reach Settings > Screensaver > Wait Time

Return ONLY the Python code, no markdown fences."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    code = response.content[0].text.strip()
    if code.startswith("```"):
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[6:]
        code = code.strip().rstrip("```").strip()

    # Write to tests/
    test_file = Path("tests/test_roku_screensaver.py")
    test_file.write_text(code)
    print(f"   → Written to {test_file}")
    return str(test_file)


def step4_run_tests(dry_run: bool = False) -> dict:
    """Run pytest and collect results."""
    print("\n[4/5] pytest: Running Roku ECP tests...")

    if dry_run:
        print("   → [DRY RUN] Skipping pytest execution")
        return {"passed": 4, "failed": 2, "errors": 0, "report": "reports/report.html"}

    Path("reports").mkdir(exist_ok=True)
    report_path = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_roku_screensaver.py",
            "-v",
            f"--html={report_path}",
            "--self-contained-html",
            "--tb=short",
            "-x",           # stop on first failure (remove for full run)
            "--json-report",
            "--json-report-file=reports/results.json",
        ],
        capture_output=True, text=True
    )

    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)

    # Parse results
    results_file = Path("reports/results.json")
    if results_file.exists():
        with open(results_file) as f:
            data = json.load(f)
        summary = data.get("summary", {})
    else:
        summary = {}

    return {
        "passed":  summary.get("passed", 0),
        "failed":  summary.get("failed", 0),
        "errors":  summary.get("error", 0),
        "report":  report_path,
        "returncode": result.returncode,
    }


def step5_jira_recommendations(test_data: dict, test_results: dict, dry_run: bool = False):
    """Claude analyzes failures and recommends JIRA bugs."""
    print("\n[5/5] Claude: Analyzing results and generating JIRA recommendations...")

    prompt = f"""You are a QA lead reviewing test results for a Roku screensaver feature.

Test summary:
- Passed: {test_results['passed']}
- Failed: {test_results['failed']}
- Errors: {test_results['errors']}

Test cases run:
{json.dumps([tc['title'] for tc in test_data['test_cases']], indent=2)}

For each likely failure, generate a JIRA bug report. Return JSON:
{{
  "bugs": [
    {{
      "summary": "...",
      "description": "...",
      "priority": "Critical|High|Medium|Low",
      "steps_to_reproduce": "...",
      "expected_behavior": "...",
      "actual_behavior": "..."
    }}
  ],
  "overall_assessment": "..."
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()

    recommendations = json.loads(raw)
    print(f"\n   Assessment: {recommendations['overall_assessment']}")

    if not dry_run and test_results.get("failed", 0) > 0:
        jira = JiraClient()
        for bug in recommendations["bugs"]:
            desc = (
                f"Steps to reproduce: {bug['steps_to_reproduce']}\n\n"
                f"Expected: {bug['expected_behavior']}\n\n"
                f"Actual: {bug['actual_behavior']}"
            )
            created = jira.create_bug(bug["summary"], desc, bug["priority"])
            print(f"   → JIRA created: {created.get('key')} — {bug['summary']}")
    else:
        print("\n   JIRA bug recommendations (V1: review before filing):")
        for bug in recommendations["bugs"]:
            print(f"   [{bug['priority']}] {bug['summary']}")

    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Roku AI Test Automation — V1 Demo")
    parser.add_argument("--story", default=DEFAULT_STORY, help="User story text")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip actual API calls (use for testing setup)")
    args = parser.parse_args()

    print("=" * 60)
    print("  NextGen AI Test Automation — V1 Demo")
    print("  Roku Screensaver Feature")
    print("=" * 60)
    print(f"\nStory: {args.story.strip()[:120]}...")

    # Pre-flight: check Roku connectivity
    if not args.dry_run:
        roku = RokuECP(config.ROKU_IP)
        if not roku.ping():
            print(f"\n[WARNING] Cannot reach Roku at {config.ROKU_IP}")
            print("  → Tests will be skipped. Check Roku IP and WiFi.")
        else:
            print(f"\n[OK] Roku reachable at {config.ROKU_IP}")

    # Run the pipeline
    test_data    = step1_normalize_and_generate(args.story)
    testrail_ids = step2_push_to_testrail(test_data, dry_run=args.dry_run)
    test_file    = step3_generate_pytest(test_data)
    test_results = step4_run_tests(dry_run=args.dry_run)
    bugs         = step5_jira_recommendations(test_data, test_results, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)
    print(f"  TestRail suite ID : {testrail_ids['suite_id']}")
    print(f"  Generated test file: {test_file}")
    print(f"  Test results       : {test_results['passed']} passed, {test_results['failed']} failed")
    print(f"  HTML report        : {test_results['report']}")
    print(f"  JIRA bugs found    : {len(bugs['bugs'])}")
    print()


if __name__ == "__main__":
    main()
