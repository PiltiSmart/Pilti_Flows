import json
import urllib.request
import ssl
import os

# Mapping of acronyms to descriptive names
SYNC_MAP = {
    "SAT": "Smart-Attendance",
    "PD": "Presence Detectors",
    "MSL": "Motion sensor lights with Auto brightness adjustment",
    "MS": "Motion-Sensor",
    "SP": "Smart Plugs with energy monitor",
    "HB": "Heart-Beat-Monitor",
    "DB": "Smart-Door-Bell",
    "AQI": "Air-Quality-Monitor"
}

# Standardized profile name pattern
def get_profile_name(acronym):
    return f"PiltiSmart-{acronym}-Probe"

# Bypass SSL
ssl._create_default_https_context = ssl._create_unverified_context

def tb_api_call(config, url, method="GET", data=None, token=None):
    if data:
        data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'curl/8.7.1')
    if token:
        req.add_header('X-Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def sync():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/config.json"))
    with open(config_path, 'r') as f:
        config = json.load(f)

    print("--- Starting ThingsBoard Device Sync ---")
    url_login = f"{config['thingsboard']['url']}/api/auth/login"
    login_data = {
        "username": config['thingsboard']['username'],
        "password": config['thingsboard']['password']
    }
    
    try:
        token = tb_api_call(config, url_login, "POST", login_data)['token']
        print("Logged in to ThingsBoard.")
        
        # Get all devices
        dev_url = f"{config['thingsboard']['url']}/api/tenant/deviceInfos?pageSize=1000&page=0"
        devices = tb_api_call(config, dev_url, token=token)['data']
        
        # Get all profiles to find IDs
        prof_url = f"{config['thingsboard']['url']}/api/deviceProfileInfos?pageSize=1000&page=0"
        profiles_res = tb_api_call(config, prof_url, token=token)
        profile_id_map = {p['name']: p['id']['id'] for p in profiles_res['data']}

        to_delete = []
        for dev in devices:
            name = dev['name']
            
            # Step 1: Identify devices to delete (incorrect shortened names)
            if name in SYNC_MAP.keys():
                print(f"Marking for deletion: {name} ({dev['id']['id']})")
                to_delete.append(dev['id']['id'])
                
            # Step 2: Identify descriptive devices to update profiles
            for acronym, descriptive in SYNC_MAP.items():
                if name == descriptive:
                    target_profile = get_profile_name(acronym)
                    if dev['deviceProfileName'] != target_profile:
                        if target_profile in profile_id_map:
                            print(f"Updating profile for '{name}': -> {target_profile}")
                            
                            # Get full device object for update
                            full_dev_url = f"{config['thingsboard']['url']}/api/device/{dev['id']['id']}"
                            full_dev = tb_api_call(config, full_dev_url, token=token)
                            
                            # Update profile ID (Need DeviceProfileId object)
                            full_dev['deviceProfileId'] = {
                                "entityType": "DEVICE_PROFILE",
                                "id": profile_id_map[target_profile]
                            }
                            
                            # Save device (POST /api/device)
                            save_url = f"{config['thingsboard']['url']}/api/device"
                            tb_api_call(config, save_url, "POST", full_dev, token=token)
                            print(f"Successfully updated {name}")
                        else:
                            print(f"Warning: Target profile '{target_profile}' not found.")

        # Step 3: Delete incorrect devices
        for dev_id in to_delete:
            delete_url = f"{config['thingsboard']['url']}/api/device/{dev_id}"
            # Need to use DELETE method
            req = urllib.request.Request(delete_url, method='DELETE')
            req.add_header('X-Authorization', f'Bearer {token}')
            req.add_header('User-Agent', 'curl/8.7.1')
            with urllib.request.urlopen(req) as response:
                print(f"Deleted device ID: {dev_id}")

    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync()
