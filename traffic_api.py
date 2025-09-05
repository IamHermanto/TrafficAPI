from flask import Flask, jsonify, request
import subprocess
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
UNITY_SERVER_HOST = "localhost"  # Change to trafficsystem.uoa.cloud for production
UNITY_SERVER_PORT = 7777

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get Unity traffic system status"""
    try:
        # For Windows development, check WSL processes
        if os.name == 'nt':  # Windows
            try:
                # Try to check WSL process via wsl command
                result = subprocess.run(['wsl', 'pgrep', '-f', 'server.x86_64'], 
                                      capture_output=True, text=True)
                is_running = len(result.stdout.strip()) > 0
            except:
                # Fallback: assume running if we can't check
                is_running = False
        else:  # Linux
            result = subprocess.run(['pgrep', '-f', 'server.x86_64'], 
                                  capture_output=True, text=True)
            is_running = len(result.stdout.strip()) > 0
        
        return jsonify({
            "status": "running" if is_running else "stopped",
            "server": "local" if UNITY_SERVER_HOST == "localhost" else "ronin-cloud",
            "timestamp": datetime.now().isoformat(),
            "unity_host": UNITY_SERVER_HOST,
            "unity_port": UNITY_SERVER_PORT,
            "detection_method": "wsl_pgrep" if os.name == 'nt' else "pgrep"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/enable', methods=['POST'])
def enable_debug():
    """Enable debug logging in Unity traffic system"""
    try:
        # For now, this is a placeholder
        # In the future, we could send HTTP requests to Unity or write to a file
        return jsonify({
            "message": "Debug logging enabled", 
            "status": "success",
            "method": "command_line_flag",
            "note": "Restart Unity with --debug flag to enable logging"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/disable', methods=['POST'])
def disable_debug():
    """Disable debug logging in Unity traffic system"""
    try:
        return jsonify({
            "message": "Debug logging disabled", 
            "status": "success",
            "method": "command_line_flag",
            "note": "Restart Unity without --debug flag to disable logging"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/traffic/info', methods=['GET'])
def traffic_info():
    """Get traffic system information"""
    return jsonify({
        "system": "Unity Traffic Simulation",
        "version": "Digital Twin v1.0",
        "location": "Ronin Cloud Server" if UNITY_SERVER_HOST != "localhost" else "Local Development",
        "features": [
            "Vehicle AI with Physics",
            "Traffic Light Management", 
            "A* Pathfinding",
            "Intersection Detection",
            "Debug Logging",
            "Headless Server Mode"
        ],
        "capabilities": [
            "Vehicle Spawning Control",
            "Traffic Light Timing",
            "Real-time Monitoring",
            "Performance Analytics"
        ]
    })

@app.route('/api/traffic/spawn', methods=['POST'])
def spawn_vehicle():
    """Spawn a vehicle in the traffic system"""
    try:
        data = request.get_json()
        vehicle_type = data.get('type', 'default')
        location = data.get('location', 'random')
        
        return jsonify({
            "message": f"Vehicle spawned: {vehicle_type}",
            "location": location,
            "status": "success",
            "note": "This is a placeholder - Unity integration needed"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/traffic/lights', methods=['GET'])
def get_traffic_lights():
    """Get real traffic light status from Unity JSON files"""
    try:
        # Path where Unity writes status file
        if os.name == 'nt':  # Windows
            status_file = "C:/temp/unity-traffic/traffic_lights.json"
        else:  # Linux
            status_file = "/tmp/unity-traffic/traffic_lights.json"
            
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                light_data = json.load(f)
            
            return jsonify({
                "lights": [light_data],
                "source": "unity_file",
                "file_path": status_file,
                "timestamp": datetime.now().isoformat(),
                "total_lights": 1,
                "integration_status": "connected"
            })
        else:
            return jsonify({
                "error": "Unity status file not found",
                "expected_file": status_file,
                "unity_running": False,
                "integration_status": "disconnected"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/traffic/lights/<light_id>/set', methods=['POST'])
def set_traffic_light(light_id):
    """Set traffic light status"""
    try:
        data = request.get_json()
        new_status = data.get('status', 'green')
        
        if new_status not in ['red', 'yellow', 'green']:
            return jsonify({"error": "Invalid status. Use: red, yellow, green"}), 400
            
        return jsonify({
            "message": f"Traffic light {light_id} set to {new_status}",
            "light_id": light_id,
            "status": new_status,
            "success": True,
            "note": "This is a placeholder - Unity integration needed"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/server', methods=['POST'])
def configure_server():
    """Configure Unity server connection"""
    global UNITY_SERVER_HOST, UNITY_SERVER_PORT
    
    try:
        data = request.get_json()
        new_host = data.get('host', UNITY_SERVER_HOST)
        new_port = data.get('port', UNITY_SERVER_PORT)
        
        UNITY_SERVER_HOST = new_host
        UNITY_SERVER_PORT = new_port
        
        return jsonify({
            "message": "Server configuration updated",
            "host": UNITY_SERVER_HOST,
            "port": UNITY_SERVER_PORT,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "api": "Unity Traffic System Control API",
        "version": "1.0",
        "endpoints": [
            "GET /api/status - Get system status",
            "POST /api/debug/enable - Enable debug logging",
            "POST /api/debug/disable - Disable debug logging", 
            "GET /api/traffic/info - Get traffic system info",
            "POST /api/traffic/spawn - Spawn vehicle",
            "GET /api/traffic/lights - Get traffic light status",
            "POST /api/traffic/lights/<id>/set - Set traffic light",
            "POST /api/config/server - Configure server connection"
        ],
        "server": {
            "host": UNITY_SERVER_HOST,
            "port": UNITY_SERVER_PORT,
            "status": "configured"
        }
    })

if __name__ == '__main__':
    print("Starting Unity Traffic System API...")
    print(f"Unity Server: {UNITY_SERVER_HOST}:{UNITY_SERVER_PORT}")
    print("API Documentation: http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True)