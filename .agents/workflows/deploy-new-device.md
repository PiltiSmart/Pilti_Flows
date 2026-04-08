---
description: How to deploy a new device flow from scratch (crisp deployment)
---

Follow these steps to deploy a new device flow after cloning the repository.

### 1. Initial Setup
Install the required Python dependencies:
// turbo
```bash
pip install -r requirements.txt
```

### 2. Configure Connectivity
Open `config/config.json` and update the parameters for your environment:

- **ThingsBoard**:
  - `url`: Your ThingsBoard instance URL (e.g., `https://tb.yourdomain.com`).
  - `username`/`password`: Your ThingsBoard tenant/admin credentials.
  - `broker`: The MQTT broker URL (e.g., `mqtt://your-broker-ip`).
  - `device_name`: **IMPORTANT** - Set this to your new device name (e.g., "Meeting Room Sensor").
  - `profile_name`: The device profile to assign in ThingsBoard.

- **Node-RED**:
  - `url`: Your Node-RED instance URL (e.g., `https://nr.yourdomain.com`).
  - `flow_file`: The filename of the flow you want to deploy (searched in `flows/deployed/`).

### 3. Generate the Flow (Optional)
If you want to create a specialized flow based on a template, run one of the generators in `scripts/generators/`:

```bash
# Example: Generate a Presence Detector flow
python3 scripts/generators/pd_gen.py
```
This will create a new JSON file in `flows/deployed/`.

### 4. Final Deployment
Run the deployment orchestrator to provision the device in ThingsBoard and push the flow to Node-RED:

// turbo
```bash
python3 scripts/tools/deploy.py
```

### Verification
1.  **ThingsBoard**: Check the "Devices" tab; you should see your new device with an active Access Token.
2.  **Node-RED**: Open your Node-RED editor; you should see a new tab with your flow, and the MQTT nodes should be automatically configured with the correct credentials.
