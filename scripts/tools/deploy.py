#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
import os

# Bypass SSL verification for macOS Python which may lack local certificates
ssl._create_default_https_context = ssl._create_unverified_context

# Mapping of profile acronyms to original descriptive device names in ThingsBoard
ACRONYM_MAP = {
    "SAT": "Smart-Attendance",
    "PD": "Presence Detectors",
    "MSL": "Motion sensor lights with Auto brightness adjustment",
    "MS": "Motion-Sensor",
    "SP": "Smart Plugs with energy monitor",
    "HB": "Heart-Beat-Monitor",
    "DB": "Smart-Door-Bell",
    "AQI": "Air-Quality-Monitor"
}

def load_config():
    # Look for config.json in the config directory relative to the script's new location
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/config.json'))
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def tb_login(config):
    url = f"{config['thingsboard']['url']}/api/auth/login"
    payload = {
        "username": config['thingsboard']['username'],
        "password": config['thingsboard']['password']
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'curl/8.7.1')
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['token']
    except Exception as e:
        print(f"ThingsBoard Login Failed: {e}")
        return None

def tb_get_or_create_device(token, config, device_name, device_type="default"):
    # Try to find device by name
    url = f"{config['thingsboard']['url']}/api/tenant/devices?deviceName={urllib.parse.quote(device_name)}"
    req = urllib.request.Request(url)
    req.add_header('X-Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'curl/8.7.1')
    
    device_id = None
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            if res:
                device_id = res['id']['id']
                print(f"Found existing device: {device_name} ({device_id})")
    except Exception:
        pass

    if not device_id:
        # Create device
        url = f"{config['thingsboard']['url']}/api/device"
        payload = {
            "name": device_name,
            "type": device_type,
            "label": device_name
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Authorization', f'Bearer {token}')
        req.add_header('User-Agent', 'curl/8.7.1')
        
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                device_id = res['id']['id']
                print(f"Created new device: {device_name} ({device_id})")
        except Exception as e:
            print(f"Failed to create device: {e}")
            return None
    
    return device_id

def tb_get_device_credentials(token, config, device_id):
    url = f"{config['thingsboard']['url']}/api/device/{device_id}/credentials"
    req = urllib.request.Request(url)
    req.add_header('X-Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'curl/8.7.1')
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['credentialsId'] # This is the Access Token
    except Exception as e:
        print(f"Failed to get device credentials: {e}")
        return None

def deploy_flow(filepath, config):
    try:
        with open(filepath, 'r') as f:
            flow_data = json.load(f)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return

    if not isinstance(flow_data, list) or len(flow_data) == 0:
        print("Error: Invalid flow file format. Expected a JSON array.")
        return

    # Profile-Based Derivation
    flow_filename = os.path.basename(filepath)
    # Standard format: PiltiSmart-<Acronym>-Probe.json
    if flow_filename.startswith("PiltiSmart-") and flow_filename.endswith(".json"):
        derived_profile = flow_filename.replace(".json", "")
        # Derive device acronym (e.g. SAT from PiltiSmart-SAT-Probe)
        parts = derived_profile.split("-")
        if len(parts) >= 2:
            derived_device = parts[1]
        else:
            derived_device = derived_profile
    else:
        derived_profile = flow_filename.replace('_flow.json', '').replace('.json', '')
        derived_device = derived_profile

    device_name = config.get('thingsboard', {}).get('device_name')
    if not device_name:
        # Check if derived acronym has a mapping
        device_name = ACRONYM_MAP.get(derived_device, derived_device)
        
    profile_name = config.get('thingsboard', {}).get('profile_name', derived_profile)
    
    print(f"Deploying flow file: {os.path.abspath(filepath)}")
    print(f"Target Device: {device_name}")

    # ThingsBoard Workflow
    token = tb_login(config)
    if not token:
        return

    # Derive device type from profile name (defaulting to profile name if new_profile mode is active)
    device_type = profile_name if config.get('thingsboard', {}).get('new_profile', 'no').lower() == 'yes' else 'default'
    device_id = tb_get_or_create_device(token, config, device_name, device_type)
    if not device_id:
        return

    access_token = tb_get_device_credentials(token, config, device_id)
    if not access_token:
        return

    print(f"Device Access Token: {access_token}")

    # Inject Access Token and Broker Details into MQTT Broker node
    modified = False
    broker_url = config.get('thingsboard', {}).get('broker')

    for node in flow_data:
        if node.get('type') == 'mqtt-broker':
            node['credentials'] = {
                'user': access_token,
                'password': ''
            }
            if broker_url:
                parsed_url = urllib.parse.urlparse(broker_url if '://' in broker_url else f'mqtt://{broker_url}')
                if parsed_url.hostname:
                    node['broker'] = parsed_url.hostname
                if parsed_url.port:
                    node['port'] = str(parsed_url.port)
                    
            print(f"Updated MQTT Broker node '{node.get('name')}' with Access Token and Broker Details.")
            modified = True
    
    if not modified:
        print("Warning: No 'mqtt-broker' node found in flow to update.")

    # Generate new IDs to prevent "duplicate id" on redeploy
    import uuid
    id_map = {}
    
    # First pass: generate maps
    for node in flow_data:
        old_id = node.get('id')
        if old_id:
            new_id = uuid.uuid4().hex[:16]
            id_map[old_id] = new_id
    
    # Second pass: apply new ids
    for node in flow_data:
        if 'id' in node:
            node['id'] = id_map[node['id']]
        if 'z' in node and node['z'] in id_map:
            node['z'] = id_map[node['z']]
        if 'wires' in node:
            new_wires = []
            for port in node['wires']:
                new_wires.append([id_map.get(w, w) for w in port])
            node['wires'] = new_wires
        # Also handle specific property references like broker
        if 'broker' in node and node['broker'] in id_map:
            node['broker'] = id_map[node['broker']]

    # Extract tab metadata and nodes for deployment
    tab_node = flow_data[0]
    nodes = flow_data[1:]
    
    # Enforce standardized profile name as the tab label
    target_label = profile_name
    tab_node["label"] = profile_name
    
    newflow = config.get('nodered', {}).get('newflow', 'yes').lower() == 'yes'
    node_red_url = config['nodered']['url']
    
    existing_tab_id = None
    print(f"Checking for existing flow '{target_label}'...")
    try:
        req_flows = urllib.request.Request(f"{node_red_url}/flows")
        req_flows.add_header('User-Agent', 'curl/8.7.1')
        with urllib.request.urlopen(req_flows) as response:
            all_flows = json.loads(response.read().decode('utf-8'))
            for f in all_flows:
                if f.get('type') == 'tab' and f.get('label') == target_label:
                    existing_tab_id = f.get('id')
                    print(f"Found existing flow tab: {existing_tab_id}")
                    break
    except Exception as e:
        print(f"Failed to fetch existing flows: {e}")
        
    if newflow:
        if existing_tab_id:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            target_label = f"{target_label}_{timestamp}"
            print(f"Flow already exists. Appended datetime to new flow label: {target_label}")
        existing_tab_id = None
    else:
        if existing_tab_id:
            random_tab_id = tab_node.get("id")
            tab_node["id"] = existing_tab_id
            for node in nodes:
                if node.get("z") == random_tab_id:
                    node["z"] = existing_tab_id

    payload = {
        "id": tab_node.get("id"),
        "label": target_label,
        "nodes": nodes
    }
    
    data = json.dumps(payload).encode('utf-8')
    if existing_tab_id:
        url = f"{node_red_url}/flow/{existing_tab_id}"
        req = urllib.request.Request(url, data=data, method='PUT')
    else:
        url = f"{node_red_url}/flow"
        req = urllib.request.Request(url, data=data, method='POST')
        
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'curl/8.7.1')
    
    print(f"Deploying to Node-RED at {url}...")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            print(f"Success! Flow deployed with response: {res_body}")
    except urllib.error.HTTPError as e:
        print(f"Failed to deploy. HTTP Code: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Failed to deploy: {e}")

if __name__ == "__main__":
    config = load_config()
    
    if len(sys.argv) < 2:
        filepath = config.get('nodered', {}).get('flow_file')
        if not filepath:
            print("Usage: python3 deploy.py <flow_file.json> (or specify in config.json)")
            sys.exit(1)
    else:
        filepath = sys.argv[1]
        
    # If the filepath is a simple filename and doesn't exist locally,
    # try looking in all subdirectories of the flows/ directory
    if not os.path.exists(filepath) and not os.path.isabs(filepath):
        flows_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../flows/'))
        found = False
        for root, dirs, files in os.walk(flows_root):
            if filepath in files:
                filepath = os.path.join(root, filepath)
                found = True
                break
        if not found:
            # Fallback to templates if still not found
            templates_path = os.path.join(flows_root, 'templates', filepath)
            if os.path.exists(templates_path):
                filepath = templates_path

    deploy_flow(filepath, config)
