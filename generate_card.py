import os
import requests

GITHUB_TOKEN = os.getenv("GH_TOKEN")
USERNAME = os.getenv("GH_USERNAME")

def fetch_github_stats():
    query = """
    query($username: String!) {
      user(login: $username) {
        repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR]) {
          totalCount
          nodes {
            stargazerCount
          }
        }
        repositoriesContributedTo(first: 100) {
          totalCount
        }
        followers {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"username": USERNAME}},
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"API hatasi: {response.status_code} - {response.text}")
        
    data = response.json()["data"]["user"]
    
    total_repos = data["repositories"]["totalCount"]
    total_stars = sum(repo["stargazerCount"] for repo in data["repositories"]["nodes"])
    contributed = data["repositoriesContributedTo"]["totalCount"]
    total_followers = data["followers"]["totalCount"]
    total_commits = data["contributionsCollection"]["totalCommitContributions"]
    
    return {
        "repos": str(total_repos),
        "stars": str(total_stars),
        "contributed": str(contributed),
        "followers": str(total_followers),
        "commits": f"{total_commits:,}",
    }

def main():
    stats = fetch_github_stats()
    
    # Kendi profil bilgilerine gore burayi duzenle
    stats.update({
        "username": USERNAME if USERNAME else "user",
        "os_info": "Arch Linux x86_64",
        "host_info": "Lenovo LOQ 15IRX10",
        "kernel_info": "Linux 6.x",
        "ide_info": "Neovim / VSCode",
        "languages_prog": "Go, Rust, Python, C++",
        "languages_real": "Turkish, English",
        "hobbies": "Open Source, Backend Dev",
        "email": "kullanici@domain.com",
        "linkedin": "in/kullaniciadi",
        "loc_total": "250,420",
        "loc_add": "310,120",
        "loc_del": "59,700"
    })

    with open("templates/card_template.svg", "r", encoding="utf-8") as f:
        template = f.read()

    output_svg = template.format(**stats)

    with open("output_card.svg", "w", encoding="utf-8") as f:
        f.write(output_svg)

if __name__ == "__main__":
    main()