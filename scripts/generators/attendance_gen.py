import json
import os

# Use absolute path relative to script location for templates and deployed flows
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/templates/Motion_Sensor_flow.json"))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../flows/smart_office/Smart_attendence_tracker_flow.json"))

with open(template_path, 'r') as f:
    flow = json.load(f)

for node in flow:
    if node.get("type") == "tab":
        node["label"] = "Smart Attendance Tracker-Flow"
    
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
