#app.py
from flask import Flask, request, jsonify
import time
import json
import logging
import os
from datetime import datetime, timedelta
import csv

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# In-memory database
containers = {}
items = {}
system_logs = []
current_time = datetime.now()

# Helper function to log actions
def log_action(action, details):
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "details": details
    }
    system_logs.append(log_entry)
    logger.info(f"{action}: {details}")

# Root endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Space Station Cargo Management System API"}), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# 1. Placement API (basic placement functionality)
@app.route('/api/placement', methods=['POST'])
def placement():
    try:
        data = request.json
        
        # Process containers
        if 'containers' in data:
            for container in data['containers']:
                container_id = container['containerId']
                containers[container_id] = container
                
        # Process items
        if 'items' in data:
            for item in data['items']:
                item_id = item['itemId']
                items[item_id] = item
                items[item_id]['containerId'] = None
                items[item_id]['position'] = None
        
        # Process placements
        placements = []
        for item_id, item in items.items():
            # Skip items that are already placed
            if item['containerId'] is not None:
                continue
                
            preferred_zone = item.get('preferredZone')
            
            # Find suitable container
            for container_id, container in containers.items():
                if container['zone'] == preferred_zone:
                    # Place item in container
                    items[item_id]['containerId'] = container_id
                    
                    # Simple placement at position (0,0,0)
                    position = {
                        "startCoordinates": [0, 0, 0],
                        "endCoordinates": [
                            item.get('width', 1),
                            item.get('depth', 1),
                            item.get('height', 1)
                        ]
                    }
                    items[item_id]['position'] = position
                    
                    # Add to placements list
                    placement = {
                        "itemId": item_id,
                        "containerId": container_id,
                        "position": position
                    }
                    placements.append(placement)
                    
                    # Log the placement
                    log_action("PLACEMENT", f"Item {item_id} placed in container {container_id}")
                    break
        
        return jsonify({
            "success": True,
            "placements": placements
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Placement API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 2. Search API
@app.route('/api/search', methods=['GET'])
def search():
    try:
        # Get query parameters
        query = request.args.get('query', '').lower()
        item_type = request.args.get('type', 'all')
        zone = request.args.get('zone')
        
        results = {
            "items": [],
            "containers": []
        }
        
        # Search items
        if item_type in ['all', 'item']:
            for item_id, item in items.items():
                # Check if item matches search criteria
                matches = (
                    (not query or 
                     query in item_id.lower() or 
                     query in item.get('name', '').lower() or
                     query in item.get('description', '').lower()) and
                    (not zone or zone in item.get('preferredZone', ''))
                )
                
                if matches:
                    results["items"].append(item)
        
        # Search containers
        if item_type in ['all', 'container']:
            for container_id, container in containers.items():
                # Check if container matches search criteria
                matches = (
                    (not query or 
                     query in container_id.lower() or 
                     query in container.get('name', '').lower() or
                     query in container.get('description', '').lower()) and
                    (not zone or zone == container.get('zone', ''))
                )
                
                if matches:
                    results["containers"].append(container)
        
        log_action("SEARCH", f"Search performed with query: {query}, type: {item_type}, zone: {zone}")
        return jsonify({
            "success": True,
            "results": results
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Search API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 3. Retrieve API
@app.route('/api/retrieve', methods=['POST'])
def retrieve():
    try:
        data = request.json
        
        if not data or 'itemId' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: itemId"
            }), 400
            
        item_id = data['itemId']
        
        # Check if item exists
        if item_id not in items:
            return jsonify({
                "success": False,
                "error": f"Item {item_id} not found"
            }), 404
            
        # Check if item is in a container
        if items[item_id]['containerId'] is None:
            return jsonify({
                "success": False,
                "error": f"Item {item_id} is not in a container"
            }), 400
            
        # Get container information
        container_id = items[item_id]['containerId']
        position = items[item_id]['position']
        
        # Remove item from container
        items[item_id]['containerId'] = None
        items[item_id]['position'] = None
        
        log_action("RETRIEVE", f"Item {item_id} retrieved from container {container_id}")
        
        return jsonify({
            "success": True,
            "retrieval": {
                "itemId": item_id,
                "containerId": container_id,
                "position": position
            }
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Retrieve API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 4. Place API (advanced placement)
@app.route('/api/place', methods=['POST'])
def place():
    try:
        data = request.json
        
        if not data or 'itemId' not in data or 'containerId' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required fields: itemId, containerId"
            }), 400
            
        item_id = data['itemId']
        container_id = data['containerId']
        coordinates = data.get('coordinates', [0, 0, 0])
        
        # Check if item exists
        if item_id not in items:
            return jsonify({
                "success": False,
                "error": f"Item {item_id} not found"
            }), 404
            
        # Check if container exists
        if container_id not in containers:
            return jsonify({
                "success": False,
                "error": f"Container {container_id} not found"
            }), 404
            
        # Get item information
        item = items[item_id]
        
        # Calculate end coordinates based on item dimensions
        end_coordinates = [
            coordinates[0] + item.get('width', 1),
            coordinates[1] + item.get('depth', 1),
            coordinates[2] + item.get('height', 1)
        ]
        
        # Place item in container
        item['containerId'] = container_id
        item['position'] = {
            "startCoordinates": coordinates,
            "endCoordinates": end_coordinates
        }
        
        log_action("PLACE", f"Item {item_id} placed in container {container_id} at {coordinates}")
        
        return jsonify({
            "success": True,
            "placement": {
                "itemId": item_id,
                "containerId": container_id,
                "position": item['position']
            }
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Place API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 5. Waste Management API
@app.route('/api/waste', methods=['POST'])
def waste_management():
    try:
        data = request.json
        
        if not data or 'itemId' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: itemId"
            }), 400
            
        item_id = data['itemId']
        
        # Check if item exists
        if item_id not in items:
            return jsonify({
                "success": False,
                "error": f"Item {item_id} not found"
            }), 404
            
        # Get container information if item is in a container
        container_id = items[item_id]['containerId']
        
        # Remove item from system
        removed_item = items.pop(item_id)
        
        log_action("WASTE", f"Item {item_id} removed from system" + 
                   (f" and container {container_id}" if container_id else ""))
        
        return jsonify({
            "success": True,
            "wasteManagement": {
                "itemId": item_id,
                "containerId": container_id,
                "status": "removed"
            }
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Waste Management API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 6. Time Simulation API
@app.route('/api/time', methods=['POST'])
def time_simulation():
    try:
        global current_time
        data = request.json
        
        if not data or 'hours' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: hours"
            }), 400
            
        hours = data['hours']
        
        # Advance time
        current_time += timedelta(hours=hours)
        
        # Simulate time effects on items (e.g., perishable items)
        affected_items = []
        for item_id, item in list(items.items()):
            # Example: If an item is perishable and its expiry is passed, handle it
            if item.get('perishable') and item.get('expiryDate'):
                expiry_date = datetime.fromisoformat(item['expiryDate'])
                if current_time > expiry_date:
                    # Mark item as expired
                    item['status'] = 'expired'
                    affected_items.append({
                        "itemId": item_id,
                        "status": "expired",
                        "action": "marked"
                    })
        
        log_action("TIME", f"Time advanced by {hours} hours to {current_time.isoformat()}")
        
        return jsonify({
            "success": True,
            "timeSimulation": {
                "currentTime": current_time.isoformat(),
                "hoursAdvanced": hours,
                "affectedItems": affected_items
            }
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Time Simulation API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 7. Import API
@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        global containers, items
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided for import"
            }), 400
            
        # Import containers
        if 'containers' in data:
            for container in data['containers']:
                if 'containerId' in container:
                    containers[container['containerId']] = container
        
        # Import items
        if 'items' in data:
            for item in data['items']:
                if 'itemId' in item:
                    items[item['itemId']] = item
        
        total_containers = len(containers)
        total_items = len(items)
        
        log_action("IMPORT", f"Imported {len(data.get('containers', []))} containers and {len(data.get('items', []))} items")
        
        return jsonify({
            "success": True,
            "import": {
                "containersImported": len(data.get('containers', [])),
                "itemsImported": len(data.get('items', [])),
                "totalContainers": total_containers,
                "totalItems": total_items
            }
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Import API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 8. Export API
@app.route('/api/export', methods=['GET'])
def export_data():
    try:
        export_type = request.args.get('type', 'all')
        
        export_data = {}
        
        if export_type in ['all', 'containers']:
            export_data['containers'] = list(containers.values())
            
        if export_type in ['all', 'items']:
            export_data['items'] = list(items.values())
        
        log_action("EXPORT", f"Exported data of type: {export_type}")
        
        return jsonify({
            "success": True,
            "export": export_data
        }), 200
        
    except Exception as e:
        log_action("ERROR", f"Export API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 9. Logs API
@app.route('/api/logs', methods=['GET'])
def logs():
    try:
        # Get optional filter parameters
        action_filter = request.args.get('action')
        limit = request.args.get('limit')
        
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                limit = None
        
        # Apply filters
        filtered_logs = system_logs
        
        if action_filter:
            filtered_logs = [log for log in filtered_logs if log['action'] == action_filter]
            
        # Apply limit
        if limit:
            filtered_logs = filtered_logs[-limit:]
        
        return jsonify({
            "success": True,
            "logs": filtered_logs
        }), 200
        
    except Exception as e:
        logger.error(f"Logs API error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Run the application
if __name__ == '__main__':
    log_action("STARTUP", "Space Station Cargo Management System starting up")
    app.run(host='0.0.0.0', port=8000, debug=True)
