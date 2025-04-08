import os
import requests

# Get GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_CUSTOM")
ORG_NAME = "openpitrix"  # Replace with your organization name

# GraphQL endpoint
url = "https://api.github.com/graphql"

# Define headers for requests
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

# Query to get all repositories in the organization
repo_query = """
query($org: String!) {
  organization(login: $org) {
    repositories(first: 100) {
      nodes {
        name
      }
    }
  }
}
"""

# Request to fetch repositories
def get_repositories():
    variables = {
        "org": ORG_NAME
    }
    response = requests.post(url, json={"query": repo_query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        if data.get("data") and data["data"].get("organization"):
            repos = [repo["name"] for repo in data["data"]["organization"]["repositories"]["nodes"]]
            return repos
        else:
            print(f"Error: Data not found in the response")
            print(f"Response: {data}")
            return []
    else:
        print(f"Failed to fetch repositories: {response.status_code}")
        print(f"Response: {response.text}")
        return []

# Query to get reviewers for a specific repository
pr_query = """
query($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(last: 5) {
      nodes {
        reviewRequests(first: 10) {
          nodes {
            requestedReviewer {
              ... on User {
                login
              }
            }
          }
          }
          }
        }
      }
    }
  }
}
"""

# Request to fetch reviewers for each PR
def get_pull_request_reviewers(owner, repo):
    variables = {
        "owner": owner,
        "repo": repo
    }
    response = requests.post(url, json={"query": pr_query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(response.json())
        if data.get("data") and data["data"].get("repository"):
            reviewers_data = []
            for pr in data["data"]["repository"]["pullRequests"]["nodes"]:
                pr_reviewers = []
                for review in pr["reviews"]["nodes"]:
                    pr_reviewers.append({
                        "login": review["user"]["login"],
                        "state": review["state"]
                    })
                reviewers_data.append(pr_reviewers)
            return reviewers_data
        else:
            print(f"Error: No PR data found for repository: {repo}")
            return []
    else:
        print(f"Failed to fetch PRs for {repo}: {response.status_code}")
        print(f"Response: {response.text}")
        return []

# Main logic
def main():
    repositories = get_repositories()

    if repositories:
        for repo in repositories:
            print(f"\nFetching reviewers for repository: {repo}")
            reviewers_data = get_pull_request_reviewers(ORG_NAME, repo)
            
            if reviewers_data:
                for pr_reviewers in reviewers_data:
                    if pr_reviewers:
                        print("Reviewers:")
                        for reviewer in pr_reviewers:
                            print(f"- {reviewer['login']} (State: {reviewer['state']})")
                    else:
                        print("No reviewers found for this PR.")
            else:
                print(f"No pull requests found for {repo}")
    else:
        print("No repositories found or an error occurred.")

if __name__ == "__main__":
    main()


