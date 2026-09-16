import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests

REPORT_PATH = Path("report.json")
RESULTS_PATH = Path("results.json")
MAP_PATH = Path("github_moodle_map.csv")


def compute_score() -> dict:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    summary = report.get("summary", {})
    total = int(summary.get("total", 0))
    passed = int(summary.get("passed", 0))
    failed = int(summary.get("failed", 0))
    errors = int(summary.get("error", 0))

    max_score = 100
    score = round((passed / total) * max_score, 2) if total else 0.0

    result = {
        "github_username": resolve_github_username(),
        "assignment": os.getenv("ASSIGNMENT_NAME", "Unknown Assignment"),
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": total,
    }

    RESULTS_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


def get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def resolve_github_username() -> str:
    """
    Resolve real student GitHub username.

    GitHub Classroom may trigger workflows as github-classroom[bot].
    If that happens, we extract the username from the repo name.

    Example:
        fm3-python-programming-davmoha -> davmoha
    """

    invalid_users = {
        "github-classroom[bot]",
        "github-actions[bot]",
        "izen-academy",
    }

    candidates = [
        os.getenv("GITHUB_USERNAME", "").strip(),
        os.getenv("GITHUB_ACTOR", "").strip(),
    ]

    for candidate in candidates:
        if candidate and candidate.lower() not in invalid_users:
            return candidate

    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    repo_name = repo.split("/", 1)[1] if "/" in repo else repo

    assignment_slug = os.getenv("ASSIGNMENT_SLUG", "").strip()

    if assignment_slug:
        prefix = f"{assignment_slug}-"
        if repo_name.startswith(prefix):
            return repo_name[len(prefix):]

    if "-" in repo_name:
        return repo_name.split("-")[-1]

    raise RuntimeError(
        "Could not determine GitHub username. "
        f"GITHUB_REPOSITORY={repo}"
    )


def lookup_moodle_student_id(github_username: str, course_id: str) -> Optional[str]:
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"Mapping file not found: {MAP_PATH}")

    with MAP_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required_columns = {"github_username", "moodle_student_id", "course_id"}
        missing = required_columns - set(reader.fieldnames or [])

        if missing:
            raise RuntimeError(
                f"{MAP_PATH} is missing required columns: {', '.join(sorted(missing))}"
            )

        matches = []

        for row in reader:
            if (
                row.get("github_username", "").strip().lower()
                == github_username.strip().lower()
                and row.get("course_id", "").strip()
                == str(course_id).strip()
            ):
                matches.append(row)

    if not matches:
        return None

    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple Moodle mappings found for GitHub user '{github_username}' "
            f"in course '{course_id}'. Keep only one row per user per course."
        )

    student_id = matches[0].get("moodle_student_id", "").strip()

    if not student_id:
        raise RuntimeError(
            f"Blank Moodle student id for GitHub user '{github_username}' "
            f"in course '{course_id}'"
        )

    return student_id


def validate_moodle_response(response: requests.Response) -> None:
    print("Response status:", response.status_code)
    print("Response body:", response.text)

    response.raise_for_status()

    try:
        body = response.json()
    except ValueError:
        raise RuntimeError("Moodle returned a non-JSON response.")

    if isinstance(body, dict) and body.get("exception"):
        raise RuntimeError(
            f"Moodle API error: {body.get('errorcode', 'unknown')} - "
            f"{body.get('message', 'No message returned')}"
        )


def sync_score() -> None:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError("results.json not found. Run compute mode first.")

    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    moodle_url = get_required_env("MOODLE_URL")
    moodle_token = get_required_env("MOODLE_TOKEN")
    course_id = get_required_env("MOODLE_COURSE_ID")
    activity_id = get_required_env("MOODLE_ACTIVITY_ID")

    github_username = resolve_github_username()
    print(f"Resolved GitHub username: {github_username}")

    student_id = lookup_moodle_student_id(github_username, course_id)

    if not student_id:
        raise RuntimeError(
            f"No Moodle student id found for GitHub user '{github_username}' "
            f"in course '{course_id}'"
        )

    payload = {
        "wstoken": moodle_token,
        "wsfunction": "core_grades_update_grades",
        "moodlewsrestformat": "json",
        "source": "mod/assign",
        "courseid": course_id,
        "component": "mod_assign",
        "activityid": activity_id,
        "itemnumber": 0,
        "grades[0][studentid]": student_id,
        "grades[0][grade]": float(results["score"]),
    }

    print("Sending Moodle payload:")
    for key, value in payload.items():
        if key == "wstoken":
            print(f"{key}: ***")
        else:
            print(f"{key}: {value}")

    response = requests.post(moodle_url, data=payload, timeout=30)
    validate_moodle_response(response)

    print("Grade sync completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["compute", "sync"], required=True)
    args = parser.parse_args()

    if args.mode == "compute":
        compute_score()
    else:
        sync_score()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
