import subprocess
import sys
import os
from github import Github
from git import Repo


def run_command(command):
    """Run a shell command and capture its output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout


def create_pull_request(repo, backport_branch, target_branch, pr_title, pr_body):
    """Create a pull request on GitHub."""
    try:
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            base=target_branch,
            head=backport_branch
        )
        print(f"Created pull request: {pr.html_url}")
    except Exception as e:
        print(f"Error creating PR: {str(e)}")
        sys.exit(1)


def main():
    pr_number = sys.argv[1]  # PR number passed from GitHub Actions
    target_branch = sys.argv[2]  # Target branch (e.g., '2.0')
    github_token = sys.argv[3]  # GitHub token for authentication

    # Set up GitHub and repo
    g = Github(github_token)
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

    # Set up local Git repo
    repo_path = os.getcwd()
    local_repo = Repo(repo_path)

    # Run cherry-picker
    print("Running cherry-picker...")
    cherry_pick_log = run_command(f"cherry_picker 3253d691f0f5fec668a25ec5932187f9600b3440 2.0")
    print(cherry_pick_log)

    # Extract backport branch from cherry-pick log
    backport_branch = None
    for line in cherry_pick_log.splitlines():
        if 'backport-' in line:  # Adjust the condition based on your cherry-pick output
            backport_branch = line.split()[-1]
            break

    # if not backport_branch:
    #     print("Backport branch not found.")
    #     sys.exit(1)

    print(f"Backport branch: {backport_branch}")

    # # Create and push the backport branch
    # print("Creating and pushing backport branch...")
    # local_repo.git.checkout('HEAD', b=backport_branch)  # Create the backport branch
    run_command(f"git push")

    # Create the pull request
    pr_title = f"Backport of PR #{pr_number} to {target_branch}"
    pr_body = f"Automated backport of PR #{pr_number} from main to {target_branch}."
    create_pull_request(repo, backport_branch, target_branch, pr_title, pr_body)

    # Optionally, delete the backport branch after PR is created
    # print("Deleting backport branch...")
    # run_command(f"git push origin --delete {backport_branch}")

    print("Backport process completed successfully!")


if __name__ == "__main__":
    main()
