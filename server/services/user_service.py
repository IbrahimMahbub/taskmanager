from flask import Blueprint, request, jsonify
import os
from server.services.utils import generate_id, load_json_safe, save_json_safe

user_bp = Blueprint("user", __name__)

USER_DB = os.path.join("server", "data", "users.json")

# Ensure the database file exists
if not os.path.exists("server/data"):
    os.makedirs("server/data")
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)  # Create an empty users file if it doesn't exist

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Load existing users from the database
    users = load_json_safe(USER_DB)

    # Generate a unique user ID using the utility function
    user_id = generate_id()

    # Add the new user to the users dictionary
    users[user_id] = {"id": user_id, "name": username}

    # Save the updated users dictionary back to the database
    save_json_safe(USER_DB, users)

    # Return the user ID and username as a response
    return jsonify({"user_id": user_id, "username": username}), 201

@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Load users from the database
    users = load_json_safe(USER_DB)

    # Check if the user exists
    user = users.get(user_id)

    if user:
        return jsonify({"user_id": user["id"], "username": user["name"]}), 200
    else:
        return jsonify({"error": "Invalid User ID"}), 404

@user_bp.route("/validate", methods=["POST"])
def validate_user():
    data = request.json
    user_id = data.get("user_id")

    # Load users from the database
    users = load_json_safe(USER_DB)

    # Check if the user ID exists in the database
    if user_id in users:
        return jsonify({"valid": True, "name": users[user_id]["name"]}), 200
    else:
        return jsonify({"valid": False}), 404

@user_bp.route("/list", methods=["GET"])
def list_users():
    # Load all users from the database
    users = load_json_safe(USER_DB)

    # Return the list of users
    return jsonify(users), 200
