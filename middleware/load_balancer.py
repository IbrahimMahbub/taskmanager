from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# List of available server instances
servers = []

@app.route("/register", methods=["POST"])
def register_server():
    """Register a new server with the middleware"""
    data = request.json
    host = data.get("host")
    port = data.get("port")

    if not host or not port:
        return jsonify({"error": "host and port required"}), 400

    server = {"host": host, "port": port}

    # Register the server if it's not already in the list
    if server not in servers:
        servers.append(server)
        print(f"[+] Registered new server: {host}:{port}")
    else:
        print(f"[!] Server {host}:{port} is already registered.")
    
    return jsonify({"message": "Server registered"}), 200

@app.route("/connect", methods=["GET"])
def connect():
    """Provide a server address to the client"""
    if not servers:
        return jsonify({"error": "No available servers"}), 500

    # Randomly select a server from the list of registered servers
    selected_server = random.choice(servers)
    return jsonify(selected_server), 200

# Optional: for debugging
@app.route("/servers", methods=["GET"])
def list_servers():
    """List all registered servers"""
    return jsonify(servers), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint to ensure the middleware is running."""
    return jsonify({"status": "Healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
