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

# Query to get PR titles and reviewers for a specific repository
pr_query = """
query($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(last: 5) {
      nodes {
        title
        reviews(last: 5) {
          nodes {
            user {
              login
            }
            state
          }
        }
      }
    }
  }
}
"""

# Request to fetch PR titles and reviewers
def get_pull_requests(owner, repo):
    variables = {
        "owner": owner,
        "repo": repo
    }
    response = requests.post(url, json={"query": pr_query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if data.get("data") and data["data"].get("repository"):
            pr_data = []
            for pr in data["data"]["repository"]["pullRequests"]["nodes"]:
                pr_info = {
                    "title": pr["title"],
                    "reviewers": []
                }
                for review in pr["reviews"]["nodes"]:
                    pr_info["reviewers"].append({
                        "login": review["user"]["login"],
                        "state": review["state"]
                    })
                pr_data.append(pr_info)
            return pr_data
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
            print(f"\nFetching PR titles and reviewers for repository: {repo}")
            pr_data = get_pull_requests(ORG_NAME, repo)
            
            if pr_data:
                for pr in pr_data:
                    print(f"PR Title: {pr['title']}")
                    if pr["reviewers"]:
                        print("Reviewers:")
                        for reviewer in pr["reviewers"]:
                            print(f"- {reviewer['login']} (State: {reviewer['state']})")
                    else:
                        print("No reviewers found for this PR.")
            else:
                print(f"No pull requests found for {repo}")
    else:
        print("No repositories found or an error occurred.")

if __name__ == "__main__":
    main()

