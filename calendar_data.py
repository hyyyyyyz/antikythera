"""Read the daily public commit contributions that GitHub credits to a user."""

from collections import Counter
from datetime import date, timedelta
import json
import subprocess


QUERY = """
query Calendar($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        repository { visibility }
        contributions(first: 100) {
          pageInfo { hasNextPage }
          nodes { occurredAt commitCount }
        }
      }
    }
  }
}
"""


def fetch_groups(username, start, end):
    variables = {"login": username, "from": f"{start}T00:00:00Z", "to": f"{end}T23:59:59Z"}
    response = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=json.dumps({"query": QUERY, "variables": variables}),
        capture_output=True, text=True, check=False, timeout=90,
    )
    if response.returncode:
        raise RuntimeError(response.stderr.strip() or "GitHub GraphQL request failed")
    payload = json.loads(response.stdout)
    if payload.get("errors"):
        raise RuntimeError("; ".join(error["message"] for error in payload["errors"]))
    user = payload["data"]["user"]
    if user is None:
        raise ValueError(f"GitHub user {username!r} was not found")
    return user["contributionsCollection"]["commitContributionsByRepository"]


def daily_commits(username, start, end, fetch=fetch_groups):
    counts = Counter()

    def read_window(first, last):
        groups = fetch(username, first, last)
        if len(groups) >= 100 or any(g["contributions"]["pageInfo"]["hasNextPage"] for g in groups):
            if first == last:
                raise ValueError(f"GitHub's contribution limits prevent a complete count on {first}")
            middle = first + (last - first) // 2
            read_window(first, middle)
            read_window(middle + timedelta(days=1), last)
            return
        for group in groups:
            if group["repository"]["visibility"] == "PUBLIC":
                for node in group["contributions"]["nodes"]:
                    day = date.fromisoformat(node["occurredAt"][:10])
                    if first <= day <= last:
                        counts[day] += node["commitCount"]

    # A repository can contribute one node per day. Stay below the 100-node page.
    first = start
    while first <= end:
        last = min(first + timedelta(days=89), end)
        read_window(first, last)
        first = last + timedelta(days=1)
    return counts
