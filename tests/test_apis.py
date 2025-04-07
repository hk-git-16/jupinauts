#test_apis.py
import unittest
import json
import requests
import time

# Base URL for API endpoints
BASE_URL = "http://localhost:8000"

class TestSpaceStationCargoAPIs(unittest.TestCase):
    def setUp(self):
        # Wait for the server to start
        time.sleep(1)
        
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        
    def test_placement_api(self):
        # Test data
        test_data = {
            "items": [
                {
                    "itemId": "item001",
                    "name": "Food Rations",
                    "description": "Standard crew food supplies",
                    "width": 2,
                    "depth": 2,
                    "height": 1,
                    "mass": 10,
                    "preferredZone": "A"
                }
            ],
            "containers": [
                {
                    "containerId": "container001",
                    "name": "Storage Unit Alpha",
                    "description": "Primary storage unit",
                    "width": 10,
                    "depth": 10,
                    "height": 5,
                    "zone": "A"
                }
            ]
        }
        
        # Send request
        response = requests.post(f"{BASE_URL}/api/placement", json=test_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["placements"]), 1)
        self.assertEqual(data["placements"][0]["itemId"], "item001")
        self.assertEqual(data["placements"][0]["containerId"], "container001")
        
    def test_search_api(self):
        # First place an item (setup)
        setup_data = {
            "items": [
                {
                    "itemId": "item002",
                    "name": "Medical Supplies",
                    "description": "First aid kit",
                    "preferredZone": "B"
                }
            ],
            "containers": [
                {
                    "containerId": "container002",
                    "name": "Medical Storage",
                    "description": "Medical supplies storage",
                    "zone": "B"
                }
            ]
        }
        requests.post(f"{BASE_URL}/api/placement", json=setup_data)
        
        # Test search by term
        response = requests.get(f"{BASE_URL}/api/search?query=medical")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue("items" in data["results"])
        self.assertTrue("containers" in data["results"])
        
        # At least one item and one container should be found
        self.assertGreaterEqual(len(data["results"]["items"]), 1)
        self.assertGreaterEqual(len(data["results"]["containers"]), 1)
        
    def test_retrieve_api(self):
        # First place an item (setup)
        setup_data = {
            "items": [
                {
                    "itemId": "item003",
                    "name": "Tool Kit",
                    "description": "Maintenance tools",
                    "preferredZone": "C"
                }
            ],
            "containers": [
                {
                    "containerId": "container003",
                    "name": "Tool Storage",
                    "description": "Tool storage unit",
                    "zone": "C"
                }
            ]
        }
        requests.post(f"{BASE_URL}/api/placement", json=setup_data)
        
        # Now retrieve the item
        retrieve_data = {
            "itemId": "item003"
        }
        response = requests.post(f"{BASE_URL}/api/retrieve", json=retrieve_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["retrieval"]["itemId"], "item003")
        self.assertEqual(data["retrieval"]["containerId"], "container003")
        
    def test_place_api(self):
        # First create an item and container (setup)
        setup_data = {
            "items": [
                {
                    "itemId": "item004",
                    "name": "Oxygen Tank",
                    "description": "Spare oxygen",
                    "width": 1,
                    "depth": 1,
                    "height": 3
                }
            ],
            "containers": [
                {
                    "containerId": "container004",
                    "name": "Oxygen Storage",
                    "description": "Oxygen storage unit",
                    "zone": "D"
                }
            ]
        }
        requests.post(f"{BASE_URL}/api/placement", json=setup_data)
        
        # Now place the item explicitly
        place_data = {
            "itemId": "item004",
            "containerId": "container004",
            "coordinates": [1, 1, 0]
        }
        response = requests.post(f"{BASE_URL}/api/place", json=place_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["placement"]["itemId"], "item004")
        self.assertEqual(data["placement"]["containerId"], "container004")
        self.assertEqual(data["placement"]["position"]["startCoordinates"], [1, 1, 0])
        
    def test_waste_management_api(self):
        # First create an item (setup)
        setup_data = {
            "items": [
                {
                    "itemId": "item005",
                    "name": "Waste Package",
                    "description": "Garbage to dispose"
                }
            ]
        }
        requests.post(f"{BASE_URL}/api/placement", json=setup_data)
        
        # Now dispose the item
        waste_data = {
            "itemId": "item005"
        }
        response = requests.post(f"{BASE_URL}/api/waste", json=waste_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["wasteManagement"]["itemId"], "item005")
        self.assertEqual(data["wasteManagement"]["status"], "removed")
        
    def test_time_simulation_api(self):
        # Advance time by 24 hours
        time_data = {
            "hours": 24
        }
        response = requests.post(f"{BASE_URL}/api/time", json=time_data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["timeSimulation"]["hoursAdvanced"], 24)
        
    def test_import_export_api(self):
        # Import data
        import_data = {
            "items": [
                {
                    "itemId": "item006",
                    "name": "Water Filter",
                    "description": "Water purification system"
                }
            ],
            "containers": [
                {
                    "containerId": "container006",
                    "name": "Water Systems Storage",
                    "description": "Water-related equipment storage",
                    "zone": "E"
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/api/import", json=import_data)
        
        # Assertions for import
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["import"]["itemsImported"], 1)
        self.assertEqual(data["import"]["containersImported"], 1)
        
        # Export data
        response = requests.get(f"{BASE_URL}/api/export")
        
        # Assertions for export
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue("containers" in data["export"])
        self.assertTrue("items" in data["export"])
        
    def test_logs_api(self):
        # Get logs
        response = requests.get(f"{BASE_URL}/api/logs")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue("logs" in data)
        self.assertIsInstance(data["logs"], list)
        
        # Test with limit
        response = requests.get(f"{BASE_URL}/api/logs?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertLessEqual(len(data["logs"]), 5)

if __name__ == '__main__':
    unittest.main()
