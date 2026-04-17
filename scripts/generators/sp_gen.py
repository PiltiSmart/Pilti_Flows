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
device_name = config['thingsboard'].get('device_name', 'SP')
profile_name = f"PiltiSmart-{device_name}-Probe"

# Use absolute path relative to script location for templates and deployed flows
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/templates/Motion_Sensor_flow.json"))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../flows/smart_home/{profile_name}.json"))

with open(template_path, "r") as f:
    flow = json.load(f)

# Metadata Comment Node Injection
acronym = "SP"
markdown = generate_markdown(acronym)

# Get tab ID for the 'z' property
tab_id = "sp_tab_01" # Default placeholder
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
        node["id"] = node["id"].replace("ms_", "sp_")
    if "z" in node and isinstance(node["z"], str) and node["z"].startswith("ms_"):
        node["z"] = node["z"].replace("ms_", "sp_")
    
    if "wires" in node:
        new_wires = []
        for w_group in node["wires"]:
            new_w_group = [w.replace("ms_", "sp_") if isinstance(w, str) and w.startswith("ms_") else w for w in w_group]
            new_wires.append(new_w_group)
        node["wires"] = new_wires
        
    if "broker" in node and isinstance(node["broker"], str) and node["broker"].startswith("ms_"):
        node["broker"] = node["broker"].replace("ms_", "sp_")

    for key in ["name", "label"]:
        if key in node and isinstance(node[key], str):
            node[key] = node[key].replace("Motion Sensor", "Smart Plugs with energy monitor")
            node[key] = node[key].replace("Motion-Sensor", "Smart-Plugs-With-Energy-Monitor")
            
    if node.get("type") == "mqtt in" and node.get("topic") == "v1/devices/me/attributes":
        node["name"] = "(Attribute)Smart-Plugs-With-Energy-Monitor"
    if node.get("type") == "mqtt out" and node.get("topic") == "v1/devices/me/attributes":
        node["name"] = "(Attributes)Smart-Plugs-With-Energy-Monitor"
    if node.get("type") == "mqtt out" and node.get("topic") == "v1/devices/me/telemetry":
        node["name"] = "(Telemetry)Smart-Plugs-With-Energy-Monitor"

    # Adapt the Telemetry Function based on device name
    if node.get("type") == "function" and "Metrics" in node.get("name", "") and "Battery" not in node.get("name", ""):
        node["func"] = """// Helper function to generate random number
function randomFloat(min, max) {
    return (Math.random() * (max - min) + min).toFixed(2);
}

// Build telemetry for this device
let out = {
    state_numeric: Math.random() > 0.5 ? 1 : 0,
    voltage_volts_numeric: parseFloat(randomFloat(220, 240)),
};

out.current_amps_numeric = out.state_numeric === 1 ? parseFloat(randomFloat(1.0, 5.0)) : 0.0;
out.power_watts_numeric = parseFloat((out.voltage_volts_numeric * out.current_amps_numeric).toFixed(2));
out.energy_consumed_kwh_numeric = parseFloat(((flow.get('energy_kwh') || 0) + (out.power_watts_numeric / 3600)).toFixed(4));
flow.set('energy_kwh', out.energy_consumed_kwh_numeric);

// Add formatted string values
out.state = out.state_numeric === 1 ? "ON" : "OFF";
out.current_amps = out.current_amps_numeric + " A";
out.voltage_volts = out.voltage_volts_numeric + " V";
out.power_watts = out.power_watts_numeric + " W";
out.energy_consumed_kwh = out.energy_consumed_kwh_numeric + " kWh";

// Set the new output in msg.payload
msg.payload = out;

// Return updated message
return msg;"""
        node["name"] = "SmartPlugMetrics"

with open(output_path, "w") as f:
    json.dump(flow, f, indent=4)
