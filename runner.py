import os
import subprocess
import yaml
import re
from urllib.parse import quote

# ---- CONFIG ---- #
YAML_FILE = "release_config.yml"
DEPLOY_DIR = os.path.join(os.getcwd(), "deployments") 

# ---- INIT ---- #
# Clear PR file at the start
with open("PR_File.txt", "w") as f:
    pass

# ---- GIT PROCESS ---- #
def run_git_command(repo_path, command):
    result = subprocess.run(command, cwd=repo_path, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[❌] Git error in {repo_path}:\n{result.stderr}")
        raise Exception(f"Git command failed: {command}")
    else:
        print(f"[✅] Git command succeeded: {command} with output: {result.stdout.strip()}")
    return result.stdout.strip()

# ---- FILE PROCESS 1---- #
def replace_tag_in_docker_file(file_path, old_tag, new_tag, pattern):
    with open(file_path, 'r') as f:
        content = f.read()
    new_content, count = re.subn(pattern.format(re.escape(old_tag)), new_tag, content)
    if count == 0:
        print(f"[⚠️] No tag replaced in: {file_path}")
    else:
        print(f"[✅] Updated tag in: {file_path}")

    with open(file_path, 'w') as f:
        f.write(new_content)

# ---- FILE PROCESS 2---- #
def replace_tag_in_cicd_file(file_path, old_tag, new_tag):
    pattern = r'(^\s*tag:\s*["\']){}(["\'])'  # allow indent and preserve quotes
    regex = re.compile(pattern.format(re.escape(old_tag)), re.MULTILINE)

    def repl(m):
        prefix = m.group(1)
        suffix = m.group(2)
        return f"{prefix}{new_tag}{suffix}"

    with open(file_path, 'r') as f:
        content = f.read()
    new_content, count = regex.subn(repl, content)
    if count == 0:
        print(f"[⚠️] No tag replaced in: {file_path}")
    else:
        print(f"[✅] Updated tag in: {file_path}")

    with open(file_path, 'w') as f:
        f.write(new_content)


# ---- MAIN ---- #
with open(YAML_FILE, 'r') as f:
    config = yaml.safe_load(f)

release_version = config["releaseTag"]
repos = {k: v for k, v in config.items() if k != "releaseTag"}

for repo_key, repo_data in repos.items():
    try:
        repo_name = repo_data["image"]["repository"]
        new_tag = repo_data["image"]["tag"]
        repo_path = os.path.join(DEPLOY_DIR, repo_name)

        if not os.path.exists(repo_path):
            print(f"[⚠️] Repo folder missing! Expected at: {repo_path}. Skipping...")
            continue

        print(f"\n🔧 Processing repo: {repo_name} with tag: {new_tag}")

        # Step 1: Check if the repo is clean
        run_git_command(repo_path, "git checkout main")
        run_git_command(repo_path, "git pull origin main")

        # Step 2: Create & switch to release branch
        run_git_command(repo_path, f"git checkout -b release_{release_version}_{repo_name}")

        # Step 3: Update Dockerfile
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

        # Step 4: Update cicd.yml
        cicd_file = os.path.join(repo_path, "cicd.yml")
        if os.path.exists(cicd_file):
            with open(cicd_file) as f:
                lines = f.readlines()

            old_tag = None
            for line in lines:
                if "tag:" in line:
                    match = re.search(r'tag:\s*["\']?([\w.\-]+)["\']?', line)
                    if match:
                        old_tag = match.group(1)
                        break

            if old_tag:
                pattern = r'(^\s*tag:\s*["\']){}(["\'])' 
                replace_tag_in_cicd_file(
                    cicd_file,
                    old_tag,
                    new_tag
                )

        # Step 5: Git add, commit, push
        run_git_command(repo_path, "git add .")
        commit_msg = f"Changes for release {release_version}"
        run_git_command(repo_path, f'git commit -m "{commit_msg}"')
        run_git_command(repo_path, f"git push origin release_{release_version}_{repo_name}")

        # Step 6: Get commit URL
        commit_hash = run_git_command(repo_path, "git rev-parse HEAD")
        origin_url = run_git_command(repo_path, "git config --get remote.origin.url")

        if origin_url.startswith("git@"):
            origin_url = origin_url.replace("git@", "https://").replace(":", "/")
        origin_url = origin_url.replace(".git", "")

        commit_url = f"{origin_url}/commit/{commit_hash}"
        pr_url = f"{origin_url}/compare/release_{quote(release_version)}_{quote(repo_name)}?expand=1"

        print(f"[✅] Commit pushed: {commit_url}")
        print(f"[🔗] Create PR: {pr_url}")

        with open("PR_File.txt", "a") as pr_file:
            pr_file.write(f"{repo_name} : {pr_url}\n")
        
        print()

    except KeyError as e:
        print(f"[❌] Missing expected key in {repo_key}: {e}")
    except Exception as e:
        print(f"[❌] Unexpected error in {repo_key}: {e}")
