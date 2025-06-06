import os
import subprocess

def clone_repo(repo_url, destination_folder):
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Change to the destination folder
    os.chdir(destination_folder)
    
    # Run the git clone command
    try:
        subprocess.run(['git', 'clone', repo_url], check=True)
        print(f"Repository cloned into {destination_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning the repository: {e}")

# Example usage
repo_url = "https://github.com/martinmimigames/tiny-music-player.git"
destination_folder = "cloned_repo"
clone_repo(repo_url, destination_folder)