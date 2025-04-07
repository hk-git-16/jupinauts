# jupinauts
IITD_National Space Hackathon
# Space Station Cargo Management System

A comprehensive system for managing cargo on a space station, developed for the National Space Hackathon 2025.

## Overview

This system provides APIs for managing items and containers on a space station, including:

- Searching for items and containers
- Retrieving items from containers
- Placing items in containers
- Managing waste
- Simulating time effects
- Importing and exporting data
- System logging

## API Endpoints

- `/api/placement` - Basic placement API for placing items in containers
- `/api/search` - Search for items and containers
- `/api/retrieve` - Retrieve items from containers
- `/api/place` - Advanced placement functionality
- `/api/waste` - Manage waste items
- `/api/time` - Simulate time effects
- `/api/import` and `/api/export` - Import/export data
- `/api/logs` - System logging

## Development Setup

1. Clone the repository:
https://github.com/hk-git-16/jupinauts

2. Install dependencies:
pip install -r requirements.txt


3. Run the application:
python app.py


4. The server will be available at `http://localhost:8000`

## Docker Setup
<!-- 
1. Build the Docker image:
docker build -t space-station-cargo 


2. Run the container: -->
<!-- docker run -p 8000:8000 space-station-cargo -->
<!-- 

3. The server will be available at `http://localhost:8000` -->

## Testing

Test the API with the provided checker script or using manual requests to the endpoints.

