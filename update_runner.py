import argparse
import os
import subprocess
import yaml
import re
from urllib.parse import quote
from datetime import datetime

# ---- FILE PATHS ---- #
YAML_FILE = "release_config.yml"
PR_FILE_PATH = "/Users/dhakshath/Desktop/PR_File.txt"
DEPLOY_DIR = os.path.join(os.getcwd(), "deployments")
LOG_FILE = "runner.log"

# ---- LOG FUNCTION ---- #


def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {msg}"
    print(full_msg)
    with open(LOG_FILE, "a") as f:
        f.write(full_msg + "\n")

# ---- GIT PROCESS ---- #


def run_git_command(repo_path, command):
    result = subprocess.run(command, cwd=repo_path,
                            shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Git error in {repo_path}:\n{result.stderr.strip()} with output: {result.stdout.strip()}")
        raise Exception(f"Git command failed: {command}")
    else:
        log(f"Git command succeeded: {command} with output: {result.stdout.strip()}")
    return result.stdout.strip()

# ---- FILE PROCESSING ---- #


def replace_tag_in_docker_file(file_path, old_tag, new_tag, pattern):
    with open(file_path, 'r') as f:
        content = f.read()
    new_content, count = re.subn(pattern.format(
        re.escape(old_tag)), new_tag, content)
    if count == 0:
        log(f"No tag replaced in Dockerfile: {file_path}")
    else:
        log(f"Updated tag in Dockerfile: {file_path}")
    with open(file_path, 'w') as f:
        f.write(new_content)


def replace_tag_in_cicd_file(file_path, old_tag, new_tag):
    pattern = r'(^\s*tag:\s*["\']){}(["\'])'
    regex = re.compile(pattern.format(re.escape(old_tag)), re.MULTILINE)

    def repl(m):
        return f"{m.group(1)}{new_tag}{m.group(2)}"

    with open(file_path, 'r') as f:
        content = f.read()
    new_content, count = regex.subn(repl, content)
    if count == 0:
        log(f"No tag replaced in cicd.yml: {file_path}")
    else:
        log(f"Updated tag in cicd.yml: {file_path}")
    with open(file_path, 'w') as f:
        f.write(new_content)

# ---- MAIN FUNCTION ---- #


def main():
    # ---- ARGUMENT PARSING ---- #
    parser = argparse.ArgumentParser(description="Run release automation")
    parser.add_argument(
        "--releasetag", help="Release tag to use for the branch", required=True)
    args = parser.parse_args()
    release_version = args.releasetag

    # ---- INIT ---- #
    with open(PR_FILE_PATH, "w") as f:
        pass  # Clear PR file at the start

    with open(YAML_FILE, 'r') as f:
        config = yaml.safe_load(f)

    repos = config

    # ---- MAIN LOGIC ---- #
    for repo_key, repo_data in repos.items():
        try:
            repo_name = repo_data["image"]["repository"]
            new_tag = repo_data["image"]["tag"]
            repo_path = os.path.join(DEPLOY_DIR, repo_name)

            if not os.path.exists(repo_path):
                log(f"Repo folder missing at: {repo_path}. Skipping...")
                continue

            log(f"Processing repo: {repo_name} with tag: {new_tag}")

            run_git_command(repo_path, "git checkout main")
            run_git_command(repo_path, "git pull origin main")

            branch_name = f"release_{release_version}_{repo_name}"
            run_git_command(repo_path, f"git checkout -b {branch_name}")

            dockerfile = os.path.join(repo_path, "Dockerfile")
            if os.path.exists(dockerfile):
                with open(dockerfile) as f:
                    first_line = f.readline().strip()
                match = re.search(r":([\w.\-]+)", first_line)
                if match:
                    old_tag = match.group(1)
                    replace_tag_in_docker_file(
                        dockerfile,
                        old_tag,
                        f":{new_tag}",
                        pattern=r":{}"
                    )
            else:
                log(f"Dockerfile not found in {repo_name}. Skipping...")
                continue

            cicd_file = os.path.join(repo_path, "cicd.yml")
            if os.path.exists(cicd_file):
                with open(cicd_file) as f:
                    lines = f.readlines()

                old_tag = None
                for line in lines:
                    if "tag:" in line:
                        match = re.search(
                            r'tag:\s*["\']?([\w.\-]+)["\']?', line)
                        if match:
                            old_tag = match.group(1)
                            break

                if old_tag:
                    replace_tag_in_cicd_file(cicd_file, old_tag, new_tag)
            else:
                log(f"cicd.yml not found in {repo_name}. Skipping...")
                continue

            log(f"Updated {dockerfile} and {cicd_file} for {repo_name}")

            run_git_command(repo_path, "git add .")
            commit_msg = f"Changes for release {release_version}"
            run_git_command(repo_path, f'git commit -m "{commit_msg}"')
            run_git_command(repo_path, f"git push origin {branch_name}")

            commit_hash = run_git_command(repo_path, "git rev-parse HEAD")
            origin_url = run_git_command(
                repo_path, "git config --get remote.origin.url")

            if origin_url.startswith("git@"):
                origin_url = origin_url.replace(
                    "git@", "https://").replace(":", "/")
            origin_url = origin_url.replace(".git", "")

            commit_url = f"{origin_url}/commit/{commit_hash}"
            pr_url = f"{origin_url}/compare/{quote(branch_name)}?expand=1"

            log(f"  ==> Commit pushed: {commit_url}")
            log(f"  ==> Create PR: {pr_url}")
            log(f"")

            with open(PR_FILE_PATH, "a") as pr_file:
                pr_file.write(f"{repo_name} : {pr_url}\n")

        except KeyError as e:
            log(f"Missing expected key in {repo_key}: {e}")
        except Exception as e:
            log(f"Unexpected error in {repo_key}: {e}")

    log(f"")
    log(f"======= Output written to: {PR_FILE_PATH} =======")
    log(f"")


# ---- ENTRY POINT ---- #
if __name__ == "__main__":
    main()
