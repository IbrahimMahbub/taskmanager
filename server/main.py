from flask import Flask, jsonify
from server.services.user_service import user_bp
from server.services.task_service import task_bp
from server.services.chat_service import chat_bp

import sys
import threading
import requests

app = Flask(__name__)

# Register all service blueprints
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(task_bp, url_prefix="/task")
app.register_blueprint(chat_bp, url_prefix="/chat")

# Health check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

# Optional: register with middleware
def register_with_middleware(server_port):
    try:
        response = requests.post(
            "http://localhost:8000/register",  # middleware must be running
            json={"host": "localhost", "port": server_port},
            timeout=3
        )
        if response.status_code == 200:
            print(f"[✓] Registered with middleware on port 8000")
        else:
            print(f"[!] Failed to register with middleware: {response.text}")
    except Exception as e:
        print(f"[!] Middleware registration error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])

    # Optional registration (can be removed if not needed)
    threading.Thread(target=register_with_middleware, args=(port,), daemon=True).start()

    # Run Flask app with threading enabled
    app.run(host="0.0.0.0", port=port, threaded=True)
