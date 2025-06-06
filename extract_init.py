import yaml
import re

def load_yaml(file_path):
    """Load YAML file and return data."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def compare_and_extract_specific_key(values_file, old_values_file, release_file):
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
                tag_match = re.search(r'(?<=hyex-init:)(\S+)', new_value)
                if tag_match:
                    tag = tag_match.group(1)
                    # Writing the output in the specified format
                    release_yaml.write(f"INIT_CONTAINER_IMAGE:\n")
                    release_yaml.write(f"  image:\n")
                    release_yaml.write(f"    repository: hyex-init\n")
                    release_yaml.write(f"    tag: '{tag}'\n")
                    release_yaml.write(f"    url: '{new_value}'\n")
                    release_yaml.write("\n")
            else:
                print("No changes detected for INIT_CONTAINER_IMAGE.")
        else:
            print("No INIT_CONTAINER_IMAGE found in the new values file.")
            return

    print(f"Changes for INIT_CONTAINER_IMAGE stored in {release_file} if there were any.")

# Usage
values_file = 'values.yaml'  # Path to the new file
old_values_file = 'old_values.yaml'  # Path to the old file
release_file = 'release.yaml'  # Path to the output file

# Run the comparison and extraction
compare_and_extract_specific_key(values_file, old_values_file, release_file)
