def generate_markdown(acronym):
    metadata = {
        "AQI": {
            "name": "Air Quality Index Monitor",
            "industry": "Environmental Health and Safety (EHS) Compliance",
            "desc": "Provides high-fidelity monitoring of critical atmospheric pollutants and overall air safety indices using real-time OpenWeatherMap data.",
            "metrics": ["aqi", "pm2_5", "pm10", "so2", "no2", "co", "o3"],
            "steps": ["Remote Config: Listens for dataIntravel attributes.", "Rate Limiting: Enforces minimum 10s interval.", "Metric Acquisition: Fetches real-time pollutants from OWM API.", "Cloud Sync: Publishes telemetry and status to ThingsBoard."]
        },
        "WL": {
            "name": "Water Level Sensor",
            "industry": "Smart Farming & Resource Management",
            "desc": "Monitors liquid levels and consumption rates in circular storage tanks using ultrasonic distance sensors.",
            "metrics": ["Water_Level(%)", "batteryLevel", "batteryStatus"],
            "steps": ["Remote Config: Dynamic reporting interval adjustment.", "Measurement: Ultrasonic distance conversion to percentage.", "Asset Tracking: Monitors tank capacity and overflow risks.", "Lifecycle: Reports battery health and power status."]
        },
        "SAT": {
            "name": "Smart Attendance Tracker",
            "industry": "Enterprise Smart Office",
            "desc": "Automated employee and student check-in system with high-precision timestamping and department categorization.",
            "metrics": ["employee_id", "department", "status", "status_numeric"],
            "steps": ["Identity Verification: Processes unique user identifiers.", "Categorization: Maps scans to departments (e.g., Engineering).", "Behavioral Analytics: Calculates confidence scores for check-ins.", "Live Sync: Updates attendance logs in real-time."]
        },
        "PD": {
            "name": "Presence Detector",
            "industry": "Smart Office / Building Automation",
            "desc": "Non-intrusive occupancy detection system using mmWave radar to distinguish between static and moving presence.",
            "metrics": ["is_present", "static_state", "moving_state", "presence_count"],
            "steps": ["Sensing: Dual-state radar monitoring (static/moving).", "Counter Logic: Tracks total occupancy in defined zones.", "Power Efficiency: Enables automated HVAC/Lighting triggers.", "Telemetry: Publishes granular presence data to ThingsBoard."]
        },
        "TH": {
            "name": "Temperature & Humidity Sensor",
            "industry": "Smart Home / Cold Chain Logistics",
            "desc": "Precision environmental monitoring for climate-sensitive zones and indoor comfort management.",
            "metrics": ["temperature", "humidity", "batteryLevel"],
            "steps": ["Environment Sensing: High-accuracy DHT/SHT simulation.", "Comfort Indexing: Provides raw data for HVAC optimization.", "Asset Protection: Real-time alerts for temp/humidity breaches.", "Health Status: Periodic battery and connectivity reporting."]
        },
        "SP": {
            "name": "Smart Plug",
            "industry": "Smart Home / Energy Management",
            "desc": "Smart socket control and real-time energy monitoring system for domestic and small-office appliances.",
            "metrics": ["power", "current", "voltage", "energy"],
            "steps": ["Energy Monitoring: Real-time telemetry of load and consumption.", "Relay Control: Supports remote on/off triggers via MQTT.", "Safety Logic: Overload protection and surge monitoring.", "Cost Analysis: Aggregated data for energy usage reporting."]
        },
        "MS": {
            "name": "Motion Sensor",
            "industry": "Smart Home Security",
            "desc": "Reactive motion detection system for security alerting and automated lighting control.",
            "metrics": ["motion", "batteryStatus"],
            "steps": ["Motion Detection: PIR/Microwave trigger-based sensing.", "Alert Management: Instant telemetry on movement events.", "Security Pairing: Logic for arming/disarming triggers.", "Lifecycle: Reports low-battery and tamper alerts."]
        },
        "MSL": {
            "name": "Motion Sensor Lights",
            "industry": "Smart Home / Interior Design",
            "desc": "Intelligent lighting system that combines motion sensitivity with ambient light thresholds (Lux).",
            "metrics": ["lux", "light_status", "motion"],
            "steps": ["Dual-Sensing: Combines movement detection with lux levels.", "Efficiency Logic: Prevents lights from turning on in daylight.", "State Management: Automated time-to-off countdowns.", "Analytics: Tracks lighting usage and energy savings."]
        },
        "HB": {
            "name": "Heart Beat Monitor",
            "industry": "Smart Hospitals / Remote Patient Monitoring",
            "desc": "Non-critical patient vital sign monitoring for BPM and blood oxygen saturation levels.",
            "metrics": ["heart_rate", "spo2", "batteryLevel"],
            "steps": ["Vitals Sensing: High-fidelity BPM and SpO2 tracking.", "Threshold Alerting: Telemetry triggers for clinical anomalies.", "Mobile Sync: Updates patient profiles on ThingsBoard.", "Continuous Ops: Low-power mode for extended wearability."]
        },
        "DB": {
            "name": "Smart Door Bell",
            "industry": "Smart Home Security",
            "desc": "Connected visitor interaction system with remote chime and presence notification.",
            "metrics": ["button_pressed", "last_ring_time", "batteryLevel"],
            "steps": ["Visitor Trigger: Instant button press event publishing.", "Event Logging: Persists last interaction timestamps.", "Remote Chime: MQTT-driven chime trigger (simulated).", "Asset Tracking: Monitors doorbell health and connectivity."]
        }
    }

    data = metadata.get(acronym)
    if not data:
        return f"### PiltiSmart {acronym} Probe\n\n**Standard IoT Device Flow**"

    metrics_md = "\n".join([f"- `{m}`" for m in data["metrics"]])
    steps_md = "\n".join([f"{i+1}. **{s.split(':')[0]}**: {s.split(':')[1].strip()}" for i, s in enumerate(data["steps"])])

    markdown = f"""### PiltiSmart {data['name']}
    
**Industry Status**: {data['industry']}.

**Description**: 
{data['desc']}

**Telemetry Metrics**:
{metrics_md}

**Lifecycle Overview**:
{steps_md}"""
    return markdown
