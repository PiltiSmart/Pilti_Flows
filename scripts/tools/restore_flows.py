import os
import sys
import json

# Add tools directory to path so we can import deploy.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from deploy import deploy_flow, load_config

def restore():
    print("Starting restoration of Node-RED flows from local JSON files...")
    
    config = load_config()
    # Force 'newflow' to 'no' to overwrite the existing empty tabs
    config['nodered']['newflow'] = 'no'
    
    # Remove static overrides to allow dynamic derivation from filenames
    if 'thingsboard' in config:
        config['thingsboard'].pop('device_name', None)
        config['thingsboard'].pop('profile_name', None)
    
    FLOWS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows"))
    
    for root, dirs, files in os.walk(FLOWS_ROOT):
        # Skip templates directory
        if "templates" in root:
            continue
            
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                print(f"\nRestoring file: {filepath}")
                try:
                    deploy_flow(filepath, config)
                    print(f"Successfully restored {filename}")
                except Exception as e:
                    print(f"Failed to restore {filename}: {e}")

if __name__ == "__main__":
    restore()
