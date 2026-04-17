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
device_name = config['thingsboard'].get('device_name', 'SAT')
profile_name = f"PiltiSmart-{device_name}-Probe"

# Use absolute path relative to script location for templates and deployed flows
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/templates/Motion_Sensor_flow.json"))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../flows/smart_office/{profile_name}.json"))

with open(template_path, 'r') as f:
    flow = json.load(f)

# Metadata Comment Node Injection
acronym = "SAT"
markdown = generate_markdown(acronym)

# Get tab ID for the 'z' property
tab_id = "sat_tab_01" # Default placeholder
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
    
    # Replace names containing 'Motion-Sensor' or 'MotionSensor'
    if "name" in node and isinstance(node["name"], str):
        node["name"] = node["name"].replace("Motion-Sensor", "Smart-Attendance-Tracker").replace("MotionSensor", "SmartAttendanceTracker")
    
    # Replace specific functions
    if node.get("name") == "SmartAttendanceTrackerMetrics":
        node["func"] = """// Helper function to generate random string
function randomStatus() {
    const statuses = ["Present", "Present", "Present", "Late", "Absent", "Half-Day"];
    return statuses[Math.floor(Math.random() * statuses.length)];
}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

let out = {
    employee_id: "EMP-" + randomInt(1000, 9999),
    department: "Engineering",
    status: randomStatus(),
    scan_timestamp: new Date().toISOString(),
    confidence_score_percent: randomInt(85, 99)
};

// Add numeric versions for dashboards
out.status_numeric = (out.status === "Present" || out.status === "Late" || out.status === "Half-Day") ? 1 : 0;

msg.payload = out;
return msg;
"""

with open(output_path, 'w') as f:
    json.dump(flow, f, indent=4)
print(f"Generated {os.path.basename(output_path)} successfully.")
