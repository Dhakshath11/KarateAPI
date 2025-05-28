import os
import re
import subprocess
from datetime import datetime

PR_FILE_PATH = "/Users/dhakshath/Desktop/PR_File.txt"
LOG_FILE = "PR_runner.log"

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {msg}"
    print(full_msg)
    with open(LOG_FILE, "a") as f:
        f.write(full_msg + "\n")

def create_prs_from_file(pr_file_path):
    if not os.path.exists(pr_file_path):
        log(f"PR file not found: {pr_file_path}")
        return

    with open(pr_file_path, "r") as file:
        for line in file:
            try:
                if ':' not in line:
                    log(f"Skipping malformed line: {line.strip()}")
                    continue

                repo_name, pr_url = line.strip().split(":", 1)
                pr_url = pr_url.strip()

                # Extract head branch from PR URL
                match = re.search(r'/compare/(release_[^?]+)', pr_url)
                if not match:
                    log(f"Could not extract branch from URL: {pr_url}")
                    continue
                head_branch = match.group(1)

                # Extract GitHub repo slug (e.g., user/repo-name)
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)/compare', pr_url)
                if not repo_match:
                    log(f"Could not extract GitHub repo from URL: {pr_url}")
                    continue
                repo_slug = repo_match.group(1)

                # Construct gh CLI command
                cmd = [
                    "gh", "pr", "create",
                    "--repo", repo_slug,
                    "--base", "main",
                    "--head", head_branch,
                    "--title", f"Release PR for {repo_name.strip()}",
                    "--body", f"Auto-generated PR for release branch `{head_branch}`"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    log(f"PR created for {repo_name.strip()} - {head_branch}")
                else:
                    log(f"Failed to create PR for {repo_name.strip()} - Error: {result.stderr.strip()}")

            except Exception as e:
                log(f"Exception while processing line: {line.strip()} - {str(e)}")

def main():
    log("=== Starting PR creation from PR_File.txt ===")
    create_prs_from_file(PR_FILE_PATH)
    log("=== Finished PR creation ===\n")

if __name__ == "__main__":
    main()
