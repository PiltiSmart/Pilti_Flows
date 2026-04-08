import json
import os

# Use absolute path relative to script location for templates and deployed flows
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/templates/Motion_Sensor_flow.json"))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/smart_office/Smart_Presence_detectors_flow.json"))

with open(template_path, "r") as f:
    flow = json.load(f)

for node in flow:
    # Rename IDs
    if "id" in node and isinstance(node["id"], str) and node["id"].startswith("ms_"):
        node["id"] = node["id"].replace("ms_", "pd_")
    if "z" in node and isinstance(node["z"], str) and node["z"].startswith("ms_"):
        node["z"] = node["z"].replace("ms_", "pd_")
    
    # Rename wires
    if "wires" in node:
        new_wires = []
        for w_group in node["wires"]:
            new_w_group = [w.replace("ms_", "pd_") if isinstance(w, str) and w.startswith("ms_") else w for w in w_group]
            new_wires.append(new_w_group)
        node["wires"] = new_wires
        
    # Rename broker references
    if "broker" in node and isinstance(node["broker"], str) and node["broker"].startswith("ms_"):
        node["broker"] = node["broker"].replace("ms_", "pd_")

    # String replacements for labels and names
    for key in ["name", "label"]:
        if key in node and isinstance(node[key], str):
            node[key] = node[key].replace("Motion Sensor", "Presence detectors")
            node[key] = node[key].replace("Motion-Sensor", "Presence-Detectors")
            
    if node.get("type") == "mqtt in" and node.get("topic") == "v1/devices/me/attributes":
        node["name"] = "(Attribute)Presence-Detectors"
    if node.get("type") == "mqtt out" and node.get("topic") == "v1/devices/me/attributes":
        node["name"] = "(Attributes)Presence-Detectors"
    if node.get("type") == "mqtt out" and node.get("topic") == "v1/devices/me/telemetry":
        node["name"] = "(Telemetry)Presence-Detectors"

    # Update the Telemetry Metrics logic explicitly based on device name
    if node.get("type") == "function" and "Metrics" in node.get("name", "") and "Battery" not in node.get("name", ""):
        node["name"] = "PresenceDetectorMetrics"
        node["func"] = """// Helper function to generate random integer in a range
function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Build telemetry tailored for Presence Detectors (e.g. mmWave sensor)
let out = {
    presence_detected_numeric: Math.random() > 0.3 ? 1 : 0, // Tends to be higher probability for mmWave
};

// If presence is detected, set a realistic distance, otherwise 0
out.target_distance_m_numeric = out.presence_detected_numeric === 1 ? parseFloat((Math.random() * 5).toFixed(2)) : 0.0;
out.illuminance_lux_numeric = randomInt(5, 500);

// Add formatted string values
out.presence_detected = out.presence_detected_numeric === 1 ? "Present" : "Clear";
out.target_distance_m = out.target_distance_m_numeric + " m";
out.illuminance_lux = out.illuminance_lux_numeric + " lux";

// Set the new output in msg.payload
msg.payload = out;

// Return updated message
return msg;"""

with open(output_path, "w") as f:
    json.dump(flow, f, indent=4)
