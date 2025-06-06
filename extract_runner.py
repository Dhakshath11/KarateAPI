import yaml
import os
import re
from datetime import datetime

# ---- FILE PATHS ---- #
VALUES_FILE = "values.yaml"
OLD_VALUES_FILE = "old_values.yaml"
RELEASE_CONFIG_FILE = "release_config.yml"
LOG_FILE = "release_config.log"

# ---- INIT LOGGING ---- #
def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {msg}"
    print(full_msg)
    with open(LOG_FILE, "a") as f:
        f.write(full_msg + "\n")

# ---- LOAD YAML FILE ---- #
def load_yaml(file_path):
    if not os.path.exists(file_path):
        log(f"File not found: {file_path}")
        return None
    with open(file_path) as f:
        return yaml.safe_load(f) or {}
    
# ---- INIT EXTRACTION ---- #
def init_tag_extraction(values_file, old_values_file, release_file):
    # Load the YAML files
    new_data = load_yaml(values_file)
    old_data = load_yaml(old_values_file)

    # Open the release.yaml file in append mode (to avoid overwriting existing file)
    with open(release_file, 'a') as release_yaml:
        # Look for the INIT_CONTAINER_IMAGE key in both new and old files
        if 'configs' in new_data.get('steward', {}) and 'INIT_CONTAINER_IMAGE' in new_data['steward']['configs']:
            new_value = new_data['steward']['configs']['INIT_CONTAINER_IMAGE']
            old_value = old_data.get('steward', {}).get('configs', {}).get('INIT_CONTAINER_IMAGE', None)
            
            # If the value has changed, extract and write it to release.yaml
            if new_value != old_value:
                # Extract the tag from the value (the part after hyex-init:)
                log(f"Change detected in INIT_CONTAINER_IMAGE:")
                log(f"  Old value: {old_value}")
                log(f"  New value: {new_value}")
                tag_match = re.search(r'(?<=hyex-init:)(\S+)', new_value)
                if tag_match:
                    tag = tag_match.group(1)
                    # Writing the output in the specified format
                    release_yaml.write(f"INIT_CONTAINER_IMAGE:\n")
                    release_yaml.write(f"  image:\n")
                    release_yaml.write(f"    repository: hyex-init\n")
                    release_yaml.write(f"    tag: {tag}\n")
                    release_yaml.write(f"    url: {new_value}\n")
                    release_yaml.write("\n")
            else:
                log("No changes detected for INIT_CONTAINER_IMAGE.")
        else:
            log("No INIT_CONTAINER_IMAGE found in the new values file.")
            return
    log(f"Changes for INIT_CONTAINER_IMAGE stored in {release_file}.")

# ---- MAIN FUNCTION ---- #
def main():
    # Check required files
    if not os.path.exists(VALUES_FILE):
        log(f"Missing required file: {VALUES_FILE}. Aborting execution.")
        return

    if not os.path.exists(OLD_VALUES_FILE):
        log(f"Missing required file: {OLD_VALUES_FILE}. Aborting execution.")
        return

    # Clear release_config.yml at start
    with open(RELEASE_CONFIG_FILE, "w") as f:
        yaml.dump({}, f)

    values_data = load_yaml(VALUES_FILE)
    old_values_data = load_yaml(OLD_VALUES_FILE)
    release_config = {}

    if values_data is None or old_values_data is None:
        log("Error loading YAML data. Aborting execution.")
        return

    for service, new_data in values_data.items():
        if "image" in new_data and isinstance(new_data["image"], dict):
            new_tag = new_data["image"].get("tag")
            if not new_tag:
                log(f"No tag found in values.yaml for '{service}'. Skipping...")
                continue

            old_tag = old_values_data.get(service, {}).get("image", {}).get("tag")

            if old_tag != new_tag:
                log(f"Change detected in '{service}':")
                log(f"  Old tag: {old_tag}")
                log(f"  New tag: {new_tag}")
                release_config[service] = {
                    "image": new_data["image"]
                }
            else:
                log(f"No change in tag for '{service}'. Skipping...")

    # Write updated release_config.yml
    with open(RELEASE_CONFIG_FILE, "w") as f:
        yaml.dump(release_config, f, sort_keys=False)
    log(f"Updated {RELEASE_CONFIG_FILE} with changed repositories.")

    # Extract INIT_CONTAINER_IMAGE tag if it exists
    init_tag_extraction(VALUES_FILE, OLD_VALUES_FILE, RELEASE_CONFIG_FILE)

    # Sync files if release_config was updated
    if release_config:
        with open(VALUES_FILE, "r") as f_new, open(OLD_VALUES_FILE, "w") as f_old:
            f_old.write(f_new.read())
        log(f"Synced {OLD_VALUES_FILE} with current {VALUES_FILE}.")
    else:
        log(f"No changes detected. {OLD_VALUES_FILE} remains unchanged.")

# ---- ENTRY POINT ---- #
if __name__ == "__main__":
    main()
    log(f"-- Done --\n")
