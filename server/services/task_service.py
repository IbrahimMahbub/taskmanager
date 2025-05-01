from flask import Blueprint, request, jsonify
import os
from server.services.utils import generate_id, load_json_safe, save_json_safe

task_bp = Blueprint("task", __name__)
TASK_DB = os.path.join("db", "tasks.json")

# Ensure DB file exists
if not os.path.exists("db"):
    os.makedirs("db")
if not os.path.exists(TASK_DB):
    save_json_safe(TASK_DB, {})

#migrate data if any mistake is in there
def migrate_owner_field():
    tasks = load_json_safe(TASK_DB)
    updated = False

    for task_id, task in tasks.items():
        if "owner" in task and "owner_id" not in task:
            task["owner_id"] = task.pop("owner")
            print(f"[Info] Migrated task {task_id}: 'owner' → 'owner_id'")
            updated = True

    if updated:
        save_json_safe(TASK_DB, tasks)
        print("[Info] Owner field migration completed.")
    else:
        print("[Info] No migration needed.")

migrate_owner_field()


# clean up malformed tasks ---
def clean_tasks():
    tasks = load_json_safe(TASK_DB)
    updated = False

    for tid, task in tasks.items():
        if "owner_id" not in task:
            print(f"[Warning] Task {tid} missing 'owner_id'. Setting to 'unknown'")
            task["owner_id"] = "unknown"
            updated = True

    if updated:
        save_json_safe(TASK_DB, tasks)
        print("[Info] Task DB cleaned.")
    else:
        print("[Info] No malformed tasks found.")

clean_tasks()
# --------------------------------------------------

@task_bp.route("/create", methods=["POST"])
def create_task():
    data = request.json
    title = data.get("title")
    owner_id = data.get("owner_id")

    if not title or not owner_id:
        return jsonify({"error": "Missing title or owner_id"}), 400

    tasks = load_json_safe(TASK_DB)
    task_id = generate_id()

    tasks[task_id] = {
        "title": title,
        "owner_id": owner_id,  # Ensure this is "owner_id"
        "status": "Pending",
        "members": [owner_id],
        "chat": []
    }
    
    save_json_safe(TASK_DB, tasks)
    return jsonify({"task_id": task_id}), 200

@task_bp.route("/get/<task_id>", methods=["GET"])
def get_task(task_id):
    tasks = load_json_safe(TASK_DB)
    task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task), 200

@task_bp.route("/list", methods=["GET"])
def list_user_tasks():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    tasks = load_json_safe(TASK_DB)
    user_tasks = []

    for tid, task in tasks.items():
        if user_id in task.get("members", []):
            user_tasks.append({
                "id": tid,
                "title": task.get("title", "Untitled"),
                "status": task.get("status", "Pending"),
                "owner_id": task.get("owner_id")  # Use .get() to avoid KeyError
            })

    return jsonify(user_tasks), 200


@task_bp.route("/status", methods=["POST"])
def update_status():
    data = request.json
    task_id = data.get("task_id")
    status = data.get("status")

    if status not in ["Pending", "In Progress", "Done"]:
        return jsonify({"error": "Invalid status"}), 400

    tasks = load_json_safe(TASK_DB)
    if task_id in tasks:
        tasks[task_id]["status"] = status
        save_json_safe(TASK_DB, tasks)
        return jsonify({"message": "Status updated"}), 200

    return jsonify({"error": "Task not found"}), 404

@task_bp.route("/assign", methods=["POST"])
def assign_user():
    data = request.json
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    actor_id = data.get("actor_id")  # must be the owner

    tasks = load_json_safe(TASK_DB)
    task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task["owner_id"] != actor_id:
        return jsonify({"error": "Only the task owner can assign members"}), 403

    if user_id not in task["members"]:
        task["members"].append(user_id)
        save_json_safe(TASK_DB, tasks)

    return jsonify({"message": "User assigned"}), 200

@task_bp.route("/remove", methods=["POST"])
def remove_user():
    data = request.json
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    actor_id = data.get("actor_id")  # must be the owner

    tasks = load_json_safe(TASK_DB)
    task = tasks.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task["owner_id"] != actor_id:
        return jsonify({"error": "Only the task owner can remove members"}), 403

    if user_id in task["members"]:
        task["members"].remove(user_id)
        save_json_safe(TASK_DB, tasks)

    return jsonify({"message": "User removed"}), 200
