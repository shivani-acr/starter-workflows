import os
import requests

# Get GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_CUSTOM")
ORG_NAME = "your_organization_name_here"  # Replace with your organization name

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
        repos = [repo["name"] for repo in data["data"]["organization"]["repositories"]["nodes"]]
        return repos
    else:
        print(f"Failed to fetch repositories: {response.status_code}")
        print(response.text)
        return []

# Query to get PR titles for a specific repository
pr_query = """
query($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(last: 5) {
      nodes {
        title
      }
    }
  }
}
"""

# Request to fetch PR titles
def get_pull_requests(owner, repo):
    variables = {
        "owner": owner,
        "repo": repo
    }
    response = requests.post(url, json={"query": pr_query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        pr_titles = [pr["title"] for pr in data["data"]["repository"]["pullRequests"]["nodes"]]
        return pr_titles
    else:
        print(f"Failed to fetch PRs for {repo}: {response.status_code}")
        print(response.text)
        return []

# Main logic
def main():
    repositories = get_repositories()

    for repo in repositories:
        print(f"\nFetching PR titles for repository: {repo}")
        pr_titles = get_pull_requests(ORG_NAME, repo)
        
        if pr_titles:
            print(f"Top 5 PR Titles in {repo}:")
            for i, title in enumerate(pr_titles, 1):
                print(f"{i}. {title}")
        else:
            print(f"No pull requests found for {repo}")

if __name__ == "__main__":
    main()
