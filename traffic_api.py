from flask import Flask, request, jsonify, render_template_string
import os
import json
import time
from datetime import datetime

app = Flask(__name__)

# Configuration
STATUS_FILE_PATH = '/tmp/unity-traffic/status.json'
COMMANDS_DIR = '/tmp/unity-traffic/commands'
UNITY_OUTPUT_DIR = '/tmp/unity-traffic'

# Ensure directories exist
os.makedirs(COMMANDS_DIR, exist_ok=True)
os.makedirs(UNITY_OUTPUT_DIR, exist_ok=True)

def read_status_file():
    """Read the current status from Unity's output file"""
    try:
        if os.path.exists(STATUS_FILE_PATH):
            with open(STATUS_FILE_PATH, 'r') as f:
                return json.load(f)
        return {"error": "Status file not found", "lights": []}
    except Exception as e:
        return {"error": str(e), "lights": []}

def write_command(command_data):
    """Write a command file for Unity to process"""
    try:
        timestamp = int(time.time() * 1000)
        command_file = os.path.join(COMMANDS_DIR, f'command_{timestamp}.json')
        with open(command_file, 'w') as f:
            json.dump(command_data, f)
        return True
    except Exception as e:
        print(f"Error writing command: {e}")
        return False

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    status = read_status_file()
    
    return jsonify({
        "status": "running" if not status.get("error") else "error",
        "timestamp": datetime.now().isoformat(),
        "total_lights": len(status.get("lights", [])),
        "server": "ronin",
        "data": status
    })

@app.route('/api/traffic/lights', methods=['GET'])
def get_traffic_lights():
    """Get all traffic lights status"""
    status = read_status_file()
    return jsonify(status)

@app.route('/api/traffic/lights/list', methods=['GET'])
def get_traffic_lights_list():
    """Get list of traffic light IDs only"""
    status = read_status_file()
    lights = status.get("lights", [])
    light_ids = [light.get("id") for light in lights]
    return jsonify({
        "count": len(light_ids),
        "light_ids": light_ids
    })

@app.route('/api/traffic/lights/<light_id>/set', methods=['POST'])
def set_traffic_light(light_id):
    """Set a specific traffic light status"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({"error": "Missing 'status' in request body"}), 400
    
    status = data['status'].lower()
    if status not in ['green', 'yellow', 'red']:
        return jsonify({"error": "Invalid status. Must be 'green', 'yellow', or 'red'"}), 400
    
    command = {
        "type": "set_light",
        "light_id": light_id,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "light_id": light_id,
            "status": status,
            "message": f"Traffic light {light_id} set to {status}"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/lights/<light_id>/mode', methods=['POST'])
def set_traffic_light_mode(light_id):
    """Set traffic light control mode (manual/automatic)"""
    data = request.get_json()
    
    if not data or 'mode' not in data:
        return jsonify({"error": "Missing 'mode' in request body"}), 400
    
    mode = data['mode'].lower()
    if mode not in ['manual', 'automatic']:
        return jsonify({"error": "Invalid mode. Must be 'manual' or 'automatic'"}), 400
    
    command = {
        "type": "set_mode",
        "light_id": light_id,
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "light_id": light_id,
            "mode": mode,
            "message": f"Traffic light {light_id} mode set to {mode}"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/lights/bulk/mode', methods=['POST'])
def set_all_lights_mode():
    """Set all traffic lights to manual or automatic mode"""
    data = request.get_json()
    
    if not data or 'mode' not in data:
        return jsonify({"error": "Missing 'mode' in request body"}), 400
    
    mode = data['mode'].lower()
    if mode not in ['manual', 'automatic']:
        return jsonify({"error": "Invalid mode. Must be 'manual' or 'automatic'"}), 400
    
    command = {
        "type": "set_all_modes",
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "mode": mode,
            "message": f"All traffic lights set to {mode} mode"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/lights/set_all_red', methods=['POST'])
def set_all_red():
    """Emergency: Set all traffic lights to red"""
    command = {
        "type": "emergency_stop",
        "status": "red",
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "message": "Emergency stop activated - all lights set to red"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/lights/set_all_green', methods=['POST'])
def set_all_green():
    """Clear all intersections: Set all traffic lights to green"""
    command = {
        "type": "clear_all",
        "status": "green",
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "message": "All intersections cleared - all lights set to green"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/lights/randomize', methods=['POST'])
def randomize_lights():
    """System test: Randomize all traffic light states"""
    command = {
        "type": "randomize",
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "message": "Traffic lights randomized for system test"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/attack/chaos', methods=['POST'])
def simulate_attack():
    """Simulate a cyber attack on the traffic system"""
    data = request.get_json() or {}
    attack_type = data.get('attack_type', 'random_chaos')
    duration = data.get('duration', 30)  # seconds
    
    command = {
        "type": "attack_simulation",
        "attack_type": attack_type,
        "duration": duration,
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "attack_type": attack_type,
            "duration": duration,
            "message": f"Cyber attack simulation started: {attack_type} for {duration} seconds"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/traffic/restore', methods=['POST'])
def restore_system():
    """Restore all traffic lights to automatic normal operation"""
    command = {
        "type": "restore_normal",
        "timestamp": datetime.now().isoformat()
    }
    
    if write_command(command):
        return jsonify({
            "success": True,
            "message": "System restored to normal automatic operation"
        })
    else:
        return jsonify({"error": "Failed to write command"}), 500

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    """Get all vehicle positions and states"""
    try:
        # Read vehicle data from Unity's output file
        vehicles_file = os.path.join(UNITY_OUTPUT_DIR, 'vehicles.json')
        
        if os.path.exists(vehicles_file):
            with open(vehicles_file, 'r') as f:
                vehicles_data = json.load(f)
            return jsonify(vehicles_data)
        else:
            return jsonify({"vehicles": []})
    except Exception as e:
        return jsonify({"error": str(e), "vehicles": []}), 500

@app.route('/dashboard')
def dashboard():
    """Web-based control dashboard"""
    dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Traffic System Control Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #1a1a1a;
            color: #fff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .status {
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        button {
            padding: 15px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-green {
            background-color: #4CAF50;
            color: white;
        }
        .btn-red {
            background-color: #f44336;
            color: white;
        }
        .btn-yellow {
            background-color: #ff9800;
            color: white;
        }
        .btn-blue {
            background-color: #2196F3;
            color: white;
        }
        button:hover {
            opacity: 0.8;
            transform: scale(1.05);
        }
        .light-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }
        .light-item {
            background-color: #2d2d2d;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .light-status {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin: 10px auto;
        }
        .status-green { background-color: #4CAF50; }
        .status-yellow { background-color: #ff9800; }
        .status-red { background-color: #f44336; }
        .mode-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-top: 5px;
        }
        .mode-auto { background-color: #2196F3; }
        .mode-manual { background-color: #9C27B0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚦 Traffic System Control Dashboard</h1>
        
        <div class="status">
            <h2>System Status</h2>
            <p>Server: <strong>Ronin</strong></p>
            <p>Total Lights: <strong id="total-lights">-</strong></p>
            <p>Last Update: <strong id="last-update">-</strong></p>
        </div>

        <h2>System Controls</h2>
        <div class="controls">
            <button class="btn-red" onclick="emergencyStop()">🛑 Emergency Stop (All Red)</button>
            <button class="btn-green" onclick="clearAll()">✅ Clear All (All Green)</button>
            <button class="btn-yellow" onclick="randomize()">🎲 Randomize (Test)</button>
            <button class="btn-blue" onclick="restore()">🔄 Restore Normal</button>
        </div>

        <h2>Traffic Lights</h2>
        <div id="lights-grid" class="light-grid">
            <p>Loading...</p>
        </div>
    </div>

    <script>
        async function updateStatus() {
            try {
                const response = await fetch('/api/traffic/lights');
                const data = await response.json();
                
                document.getElementById('total-lights').textContent = data.lights ? data.lights.length : 0;
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
                // Update lights grid
                const grid = document.getElementById('lights-grid');
                if (data.lights && data.lights.length > 0) {
                    grid.innerHTML = data.lights.map(light => `
                        <div class="light-item">
                            <strong>${light.id}</strong>
                            <div class="light-status status-${light.status}"></div>
                            <div>${light.status.toUpperCase()}</div>
                            <div class="mode-badge mode-${light.mode}">${light.mode}</div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }

        async function emergencyStop() {
            try {
                const response = await fetch('/api/traffic/lights/set_all_red', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('Emergency stop activated!');
                    setTimeout(updateStatus, 1000);
                } else {
                    alert('Emergency stop failed: ' + data.error);
                }
            } catch (error) {
                alert('Connection error: ' + error.message);
            }
        }

        async function clearAll() {
            try {
                const response = await fetch('/api/traffic/lights/set_all_green', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('All intersections cleared!');
                    setTimeout(updateStatus, 1000);
                } else {
                    alert('Clear all failed: ' + data.error);
                }
            } catch (error) {
                alert('Connection error: ' + error.message);
            }
        }

        async function randomize() {
            try {
                const response = await fetch('/api/traffic/lights/randomize', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('Lights randomized for testing!');
                    setTimeout(updateStatus, 1000);
                } else {
                    alert('Randomize failed: ' + data.error);
                }
            } catch (error) {
                alert('Connection error: ' + error.message);
            }
        }

        async function restore() {
            try {
                const response = await fetch('/api/traffic/restore', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('System restored to normal operation!');
                    setTimeout(updateStatus, 1000);
                } else {
                    alert('Restore failed: ' + data.error);
                }
            } catch (error) {
                alert('Connection error: ' + error.message);
            }
        }
        
        // Update status every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus(); // Initial load
    </script>
</body>
</html>
    """
    return render_template_string(dashboard_html)

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "api": "Unity Traffic System Control API",
        "version": "2.0",
        "description": "Cybersecurity-focused traffic system with attack simulation capabilities",
        "dashboard": "http://localhost:5000/dashboard",
        "endpoints": [
            "GET /api/status - Get system status",
            "GET /api/traffic/lights - Get all traffic lights status",
            "GET /api/traffic/lights/list - Get light IDs only",
            "POST /api/traffic/lights/<id>/set - Set traffic light status",
            "POST /api/traffic/lights/<id>/mode - Set control mode",
            "POST /api/traffic/lights/bulk/mode - Set all lights mode",
            "POST /api/traffic/lights/set_all_red - Emergency stop",
            "POST /api/traffic/lights/set_all_green - Clear all intersections",
            "POST /api/traffic/lights/randomize - Randomize for testing",
            "POST /api/traffic/attack/chaos - Simulate cyber attacks",
            "POST /api/traffic/restore - Restore normal operation",
            "GET /api/vehicles - Get all vehicle positions",
            "GET /dashboard - Web control interface"
        ]
    })

if __name__ == '__main__':
    print("Starting Unity Traffic System API...")
    print(f"API Documentation: http://localhost:5000/")
    print(f"Control Dashboard: http://localhost:5000/dashboard")
    print(f"Status File: {STATUS_FILE_PATH}")
    print(f"Command Directory: {COMMANDS_DIR}")
    print("Ready for cybersecurity demonstrations!")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=True)