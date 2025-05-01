from flask import Blueprint, request, jsonify
import os
import datetime
from server.services.utils import load_json_safe, save_json_safe

chat_bp = Blueprint("chat", __name__)
TASK_DB = os.path.join("db", "tasks.json")
USER_DB = os.path.join("data", "users.json")  # to map user_id -> username

# --- Ensure required files/directories exist ---
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists(USER_DB):
    save_json_safe(USER_DB, {})

# Optional: Clean malformed chat entries
def clean_chats():
    tasks = load_json_safe(TASK_DB)
    updated = False

    for tid, task in tasks.items():
        if not isinstance(task.get("chat"), list):
            print(f"[Warning] Task {tid} had malformed chat. Resetting to empty list.")
            task["chat"] = []
            updated = True

    if updated:
        save_json_safe(TASK_DB, tasks)
        print("[Info] Chat cleanup completed.")

clean_chats()
# ------------------------------------------------


@chat_bp.route("/send", methods=["POST"])
def send_message():
    data = request.json
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    message = data.get("message")

    if not all([task_id, user_id, message]):
        return jsonify({"error": "Missing task_id, user_id or message"}), 400

    tasks = load_json_safe(TASK_DB)
    users = load_json_safe(USER_DB)
    task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if user_id not in task["members"]:
        return jsonify({"error": "User not a member of this task"}), 403

    if not isinstance(task.get("chat"), list):
        task["chat"] = []

    # Retrieve the username from the users.json file
    user = users.get(user_id)
    if isinstance(user, dict) and "name" in user:
        username = user["name"]
    else:
        username = "Unknown"

    # Debugging logs to verify the user and username
    print(f"User ID: {user_id} - User: {user} - Username: {username}")

    # Add the new message with timestamp
    task["chat"].append({
        "user_id": user_id,
        "username": username,
        "message": message,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Save the updated tasks back
    save_json_safe(TASK_DB, tasks)
    return jsonify({"message": "Message sent"}), 200


@chat_bp.route("/get", methods=["GET"])
def get_chat():
    task_id = request.args.get("task_id")

    if not task_id:
        return jsonify({"error": "Missing task_id"}), 400

    tasks = load_json_safe(TASK_DB)
    users = load_json_safe(USER_DB)

    task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    chat_with_names = []
    for msg in task.get("chat", []):
        user_id = msg.get("user_id")
        user_info = users.get(user_id, {})
        chat_with_names.append({
            "user_id": user_id,
            "username": user_info.get("username", "Unknown"),
            "message": msg.get("message", ""),
            "timestamp": msg.get("timestamp", "")  # in case you add timestamps later
        })

    return jsonify(chat_with_names), 200



def update_existing_chat_usernames():
    tasks = load_json_safe(TASK_DB)
    users = load_json_safe(USER_DB)
    updated = False

    for task in tasks.values():
        for msg in task.get("chat", []):
            uid = msg.get("user_id")
            if msg.get("username") == "Unknown" and uid in users:
                msg["username"] = users[uid].get("username", "Unknown")
                updated = True

    if updated:
        save_json_safe(TASK_DB, tasks)
        print("[Info] Updated chat usernames where possible.")
