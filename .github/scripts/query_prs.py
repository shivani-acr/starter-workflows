# .github/scripts/query_prs.py

import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_CUSTOM")

query = """
query ($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    pullRequests(last: 5) {
      nodes {
        title
      }
    }
  }
}
"""

variables = {
    "owner": "openpitrix",
    "name": "openpitrix"
}

url = "https://api.github.com/graphql"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

print("Status Code:", response.status_code)

if response.headers.get("Content-Type", "").startswith("application/json"):
    data = response.json()
    print("Response:\n")
    for pr in data["data"]["repository"]["pullRequests"]["nodes"]:
        print("- " + pr["title"])
else:
    print("Non-JSON response:")
    print(response.text)
