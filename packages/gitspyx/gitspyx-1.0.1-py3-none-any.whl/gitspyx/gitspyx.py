import argparse
import requests
from time import sleep



def get_github_user_profile(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        profile_data = response.json()
        return profile_data
    else:
        return None

def get_github_user_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)

    if response.status_code == 200:
        repositories = response.json()


        print(f"\n\033[1;41m\033[1;37m    ..::[ Repository Detail ]::..    \033[0m\n")
        for repo in repositories:
            repo_name = repo['name']
            repo_url = repo['html_url']
            forks_count = repo['forks_count']
            stargazers_count = repo['stargazers_count']
            watchers_count = repo['watchers_count']
            issues_count = repo['open_issues_count']
            created_at = repo['created_at']
            updated_at = repo['updated_at']
            visibility = repo['private']
            has_pages = repo['has_pages']
            has_projects = repo['has_projects']
            downloads_url = repo['downloads_url']
            mirror_url = repo['mirror_url']
            license = repo['license']
            license_name = license['name'] if license else "N/A"
            license_type = license['spdx_id'] if license else "N/A"
            default_branch = repo['default_branch']
            size = repo['size']
            language = repo['language']
            is_archived = repo['archived']
            is_disabled = repo['disabled']
            is_fork = repo['fork']
            #is_locked = repo['locked']
            #is_template = repo['template']
            if 'parent' in repo:
                parent_repo = repo['parent']['full_name']
            else:
                parent_repo = "N/A"
            
            print(f"\033[1;41m\033[1;37m     ..::[ Repo: {repo_name} ]::..     \033[0m")
            print(f"\033[1;32m[+]\033[1;33m Repository Name:\033[1;32m {repo_name}")
            print(f"\033[1;32m[+]\033[1;33m Repository URL:\033[1;32m {repo_url}")
            print(f"\033[1;32m[+]\033[1;33m Forks Count:\033[1;32m {forks_count}")
            print(f"\033[1;32m[+]\033[1;33m Stargazers Count:\033[1;32m {stargazers_count}")
            print(f"\033[1;32m[+]\033[1;33m Watchers Count:\033[1;32m {watchers_count}")
            print(f"\033[1;32m[+]\033[1;33m Issues Count:\033[1;32m {issues_count}")
            print(f"\033[1;32m[+]\033[1;33m Created At:\033[1;32m {created_at}")
            print(f"\033[1;32m[+]\033[1;33m Updated At:\033[1;32m {updated_at}")
            print(f"\033[1;32m[+]\033[1;33m Visibility:\033[1;32m {'Private' if visibility else 'Public'}")
            print(f"\033[1;32m[+]\033[1;33m Has Pages:\033[1;32m {has_pages}")
            print(f"\033[1;32m[+]\033[1;33m Project URL:\033[1;32m {has_projects}")
            print(f"\033[1;32m[+]\033[1;33m Downloads URL:\033[1;32m {downloads_url}")
            print(f"\033[1;32m[+]\033[1;33m Mirror URL:\033[1;32m {mirror_url}")
            print(f"\033[1;32m[+]\033[1;33m License:\033[1;32m {license_name}")
            print(f"\033[1;32m[+]\033[1;33m License Type:\033[1;32m {license_type}")
            print(f"\033[1;32m[+]\033[1;33m Default Branch:\033[1;32m {default_branch}")
            print(f"\033[1;32m[+]\033[1;33m Size:\033[1;32m {size} KB")
            print(f"\033[1;32m[+]\033[1;33m Language:\033[1;32m {language}")
            print(f"\033[1;32m[+]\033[1;33m Is Archived:\033[1;32m {is_archived}")
            print(f"\033[1;32m[+]\033[1;33m Is Disabled:\033[1;32m {is_disabled}")
            print(f"\033[1;32m[+]\033[1;33m Is Fork:\033[1;32m {is_fork}")
            #print(f"Is Locked: {is_locked}")
            #print(f"Is Template: {is_template}")
            print(f"\033[1;32m[+]\033[1;33m Parent Repository:\033[1;32m {parent_repo}")
            print()  # Blank line for separation
            sleep(0.4)
    else:
        print(f"\033[1;31m[✗] Error: {response.status_code}")
    
def main():
    print()

bnr = """\033[1;32m╭━━━╮╭╮╭━━━╮╱╱╱╱╱╱╭━╮╭━╮
┃╭━╮┣╯╰┫╭━╮┃╱╱╱╱╱╱╰╮╰╯╭╯
┃┃╱╰╋╮╭┫╰━━┳━━┳╮╱╭╮╰╮╭╯
┃┃╭━╋┫┃╰━━╮┃╭╮┃┃╱┃┃╭╯╰╮
┃╰┻━┃┃╰┫╰━╯┃╰╯┃╰━╯┣╯╭╮╰╮
╰━━━┻┻━┻━━━┫╭━┻━╮╭┻━╯╰━╯
╱╱╱╱╱╱╱╱╱╱╱┃┃╱╭━╯┃╱╱╱╱╱
╱╱╱╱╱╱╱╱╱╱╱╰╯╱╰━━╯╱╱╱ \033[1;33mV:1.0.1
\033[1;32m╱╱╱╱╱╱╱\033[1;33mMrHacker-X\033[1;32m╱╱╱╱╱╱"""


# Set up command-line argument parser
parser = argparse.ArgumentParser(description="GitHub User Profile Details")
parser.add_argument('-u', '--username', help='GitHub username')
parser.add_argument('-r', '--repos', action='store_true',  help='Get repository detail In deep')
parser.add_argument('-v', '--version', action='store_true', help='Show script version')
parser.add_argument('-d', '--developer', action='store_true', help='Show developer name')
args = parser.parse_args()

# Check if the user requested version or developer details
if args.version:
    print("\n\033[1;37m\033[1;41m   GitSpyX Version: 1.0.1   \033[0m")

elif args.developer:
    print("\033[1;32m\nTool By MrHacker-X")
    print("\033[1;32mOwner name: Alex Butler\n")
    
else:
    if not args.username:
        parser.error('GitHub username is required.')

    # Get user profile
    profile = get_github_user_profile(args.username)

    if profile:
        print(f"{bnr}\n")
        print(f"\033[1;41m\033[1;37m   ..::[  Profile Detail Of {args.username} ]::..   \033[0m")
        print(f"\033[1;32m[+]\033[1;33m Name:\033[1;32m {profile['name']}")
        print(f"\033[1;32m[+]\033[1;33m Username:\033[1;32m {args.username}")
        print(f"\033[1;32m[+]\033[1;33m Bio:\033[1;32m {profile['bio']}")
        print(f"\033[1;32m[+]\033[1;33m Location:\033[1;32m {profile['location']}")
        print(f"\033[1;32m[+]\033[1;33m Public Repositories:\033[1;32m {profile['public_repos']}")
        print(f"\033[1;32m[+]\033[1;33m Followers:\033[1;32m {profile['followers']}")
        print(f"\033[1;32m[+]\033[1;33m Followings:\033[1;32m {profile['following']}")
        print(f"\033[1;32m[+]\033[1;33m ID:\033[1;32m {profile['id']}")
        print(f"\033[1;32m[+]\033[1;33m Public Gist:\033[1;32m {profile['public_gists']}")
        print(f"\033[1;32m[+]\033[1;33m Site Admin:\033[1;32m {profile['site_admin']}")
        print(f"\033[1;32m[+]\033[1;33m Type:\033[1;32m {profile['type']}")
        print(f"\033[1;32m[+]\033[1;33m Twitter Username:\033[1;32m {profile['twitter_username']}")
        print(f"\033[1;32m[+]\033[1;33m Blog:\033[1;32m {profile['blog']}")
        print(f"\033[1;32m[+]\033[1;33m Email:\033[1;32m {profile['email']}")
        print(f"\033[1;32m[+]\033[1;33m Profile Logo:\033[1;32m {profile['avatar_url']}")
        print(f"\033[1;32m[+]\033[1;33m Hireable:\033[1;32m {profile['hireable']}")
        print(f"\033[1;32m[+]\033[1;33m Created At:\033[1;32m {profile['created_at']}")
        print(f"\033[1;32m[+]\033[1;33m Updated At:\033[1;32m {profile['updated_at']}")

        # Add any additional profile details you want to display
        if args.repos:
            get_github_user_repositories(args.username)


        print(f"\n\033[1;41m\033[1;37m   ..::[  Mission completed ]::..   \033[0m")

    else:
        print("\n\033[1;31m[✗] User profile not found.\n")
