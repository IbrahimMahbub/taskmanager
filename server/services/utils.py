import uuid
import json
import os
from threading import Lock

lock = Lock()

# Generate a unique ID (e.g., task ID, user ID)
def generate_id(prefix="id"):
    """Generate a short, unique ID using uuid."""
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

# Load JSON data safely from a file
def load_json_safe(filepath):
    """Load JSON data from a file, return an empty dict if the file doesn't exist or is empty."""
    # Check if the file exists, if not, create it
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump({}, f)  # Initialize with an empty dictionary
    
    # Now load the file
    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # Return an empty dict if the JSON is invalid

# Save JSON data safely to a file
def save_json_safe(filepath, data):
    """Save data to a JSON file safely, using a lock."""
    with lock:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
