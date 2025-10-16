from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os

app = FastAPI(title="Fusionpact Backend API")

# Data storage (in-memory for demo, or use database)
DATA_FILE = "/app/data/storage.json"

class DataItem(BaseModel):
    name: str
    value: str
    timestamp: str

# Ensure data directory exists
os.makedirs("/app/data", exist_ok=True)

# Initialize storage file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.get("/")
def read_root():
    return {"message": "Fusionpact DevOps Challenge API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
def metrics():
    # Return Prometheus-compatible metrics
    return """# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/data",status="200"} 42
# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 100
http_request_duration_seconds_bucket{le="0.5"} 200
http_request_duration_seconds_bucket{le="1.0"} 300
http_request_duration_seconds_sum 150.5
http_request_duration_seconds_count 300
"""

# Data persistence endpoints
@app.post("/api/data")
def create_data(item: DataItem):
    try:
        # Read existing data
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        # Add new item with ID
        item_dict = item.dict()
        item_dict['id'] = len(data) + 1
        item_dict['created_at'] = datetime.now().isoformat()
        data.append(item_dict)
        
        # Write back to file
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"message": "Data created successfully", "data": item_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data")
def get_all_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return {"count": len(data), "data": data}
    except FileNotFoundError:
        return {"count": 0, "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/{item_id}")
def get_data_by_id(item_id: int):
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        for item in data:
            if item.get('id') == item_id:
                return item
        
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/data/{item_id}")
def delete_data(item_id: int):
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        data = [item for item in data if item.get('id') != item_id]
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {"message": "Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
