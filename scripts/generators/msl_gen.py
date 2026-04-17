import json
import os
import sys
# Add tools directory to path to import metadata_registry
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../tools")))
from metadata_registry import generate_markdown

# Load config to get device_name and derive profile_name (Option B)
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/config.json"))
with open(config_path, 'r') as f:
    config = json.load(f)
device_name = config['thingsboard'].get('device_name', 'MSL')
profile_name = f"PiltiSmart-{device_name}-Probe"

# Use absolute path relative to script location for templates and deployed flows
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/templates/Motion_Sensor_flow.json"))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../flows/smart_home/{profile_name}.json"))

with open(template_path, "r") as f:
    flow = json.load(f)

# Metadata Comment Node Injection
acronym = "MSL"
markdown = generate_markdown(acronym)

# Get tab ID for the 'z' property
tab_id = "msl_tab_01" # Default placeholder
for node in flow:
    if node.get("type") == "tab":
        node["label"] = profile_name
        tab_id = node.get("id")
        break

# Create and insert comment node
comment_node = {
    "id": f"{acronym.lower()}_comment_01",
    "type": "comment",
    "z": tab_id,
    "name": "Flow Description & Expansion",
    "info": markdown,
    "x": 160,
    "y": 20,
    "wires": []
}
flow.insert(1, comment_node)

for node in flow:
    if node.get("type") == "tab":
        continue
    if "id" in node and isinstance(node["id"], str) and node["id"].startswith("ms_"):
        node["id"] = node["id"].replace("ms_", "msl_")
    if "z" in node and isinstance(node["z"], str) and node["z"].startswith("ms_"):
        node["z"] = node["z"].replace("ms_", "msl_")
    
    if "wires" in node:
        new_wires = []
        for w_group in node["wires"]:
            new_w_group = [w.replace("ms_", "msl_") if isinstance(w, str) and w.startswith("ms_") else w for w in w_group]
            new_wires.append(new_w_group)
        node["wires"] = new_wires
        
    if "broker" in node and isinstance(node["broker"], str) and node["broker"].startswith("ms_"):
        node["broker"] = node["broker"].replace("ms_", "msl_")

    for key in ["name", "label"]:
        if key in node and isinstance(node[key], str):
            node[key] = node[key].replace("Motion Sensor", "Motion sensor lights with Auto brightness adjustment")
            node[key] = node[key].replace("Motion-Sensor", "Motion-Sensor-Lights-With-Auto-Brightness-Adjustment")
            
    if node.get("type") == "mqtt in" and node.get("topic") == "v1/devices/me/attributes":
        node["name"] = "(Attribute)Motion-Sensor-Lights-With-Auto-Brightness-Adjustment"
    if node.get("type") == "mqtt out" and node.get("topic") == "v1/devices/me/attributes":
        node["name"] = "(Attributes)Motion-Sensor-Lights-With-Auto-Brightness-Adjustment"
    if node.get("type") == "mqtt out" and node.get("topic") == "v1/devices/me/telemetry":
        node["name"] = "(Telemetry)Motion-Sensor-Lights-With-Auto-Brightness-Adjustment"

    # Specific logic for motion sensor lights
    if node.get("type") == "function" and "Metrics" in node.get("name", "") and "Battery" not in node.get("name", ""):
        node["func"] = """// Helper function to generate random integer
function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Build telemetry tailored for Motion sensor lights
let motion = Math.random() > 0.7 ? 1 : 0;
let ambient = randomInt(5, 800);
let state = 0;
let brightness = 0;

// Auto brightness logic
if (motion === 1) {
    state = 1;
    if (ambient < 50) brightness = 100;
    else if (ambient < 200) brightness = 75;
    else if (ambient < 500) brightness = 50;
    else brightness = 10;
}

let out = {
    motion_detected_numeric: motion,
    light_state_numeric: state,
    ambient_light_lux_numeric: ambient,
    brightness_percent_numeric: brightness,
};

// Add formatted string values
out.motion_detected = motion === 1 ? "Detected" : "Clear";
out.light_state = state === 1 ? "ON" : "OFF";
out.ambient_light_lux = ambient + " lux";
out.brightness_percent = brightness + " %";

// Set the new output in msg.payload
msg.payload = out;

// Return updated message
return msg;"""
        node["name"] = "MotionSensorLightMetrics"

with open(output_path, "w") as f:
    json.dump(flow, f, indent=4)
