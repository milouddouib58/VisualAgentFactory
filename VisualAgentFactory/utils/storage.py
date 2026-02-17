import json
import os
import uuid
from datetime import datetime

DATA_FILE = "data/projects.json"

def ensure_data_dir():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

def load_projects():
    ensure_data_dir()
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_project(name, description):
    projects = load_projects()
    new_project = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nodes": [], 
        "edges": []
    }
    projects.append(new_project)
    with open(DATA_FILE, "w") as f:
        json.dump(projects, f, indent=4)
    return new_project

def update_project_data(project_id, nodes, edges):
    projects = load_projects()
    for p in projects:
        if p["id"] == project_id:
            p["nodes"] = nodes
            p["edges"] = edges
            break
    with open(DATA_FILE, "w") as f:
        json.dump(projects, f, indent=4)

def delete_project(project_id):
    projects = load_projects()
    projects = [p for p in projects if p["id"] != project_id]
    with open(DATA_FILE, "w") as f:
        json.dump(projects, f, indent=4)
