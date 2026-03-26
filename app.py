from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import requests as req
from datetime import timedelta

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "change-this-secret-in-production"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

FRIEND_BASE_URL = "https://mini-task-management-api.onrender.com"

# --- In-memory storage (dev only) ---
USERS = {
    "waytid": {"password": "1234"},
    "admin":  {"password": "admin"},
    "กังฟู":  {"password": "veryhardpassword"}
}

TASKS: dict[str, list] = {
    "waytid": [
        {"id": 1, "title": "First task", "status": "pending"}
    ]
}


# ─── Health Check ────────────────────────────────────

@app.get("/")
def health_check():
    return jsonify({"message": "API is running"}), 200


# ─── Auth ────────────────────────────────────────────

@app.post("/auth/register")
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"msg": "username and password are required"}), 400

    if username in USERS:
        return jsonify({"msg": "User already exists"}), 400

    USERS[username] = {"password": password}
    return jsonify({"msg": f"User {username} created successfully"}), 201


@app.post("/auth/login")
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"msg": "Invalid username or password"}), 401

    token = create_access_token(identity=username)
    return jsonify(access_token=token, token_type="bearer"), 200


@app.get("/me")
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return jsonify(username=current_user), 200


# ─── Tasks (ระบบของเรา) ───────────────────────────────

@app.get("/tasks")
@jwt_required()
def list_tasks():
    user = get_jwt_identity()
    return jsonify(TASKS.get(user, [])), 200


@app.post("/tasks")
@jwt_required()
def create_task():
    user = get_jwt_identity()
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"msg": "title is required"}), 400

    user_tasks = TASKS.setdefault(user, [])
    new_id = (user_tasks[-1]["id"] + 1) if user_tasks else 1
    task = {"id": new_id, "title": title, "status": "pending"}
    user_tasks.append(task)
    return jsonify(task), 201


@app.patch("/tasks/<int:task_id>")
@jwt_required()
def update_task(task_id):
    user = get_jwt_identity()
    data = request.get_json()
    new_status = data.get("status", "").strip()
    if not new_status:
        return jsonify({"msg": "status is required"}), 400

    for task in TASKS.get(user, []):
        if task["id"] == task_id:
            task["status"] = new_status
            return jsonify(task), 200

    return jsonify({"msg": "Task not found"}), 404


@app.delete("/tasks/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    user = get_jwt_identity()
    user_tasks = TASKS.get(user, [])
    original_len = len(user_tasks)
    TASKS[user] = [t for t in user_tasks if t["id"] != task_id]

    if len(TASKS[user]) == original_len:
        return jsonify({"msg": "Task not found"}), 404

    return jsonify({"msg": f"Task {task_id} deleted"}), 200


# ─── Integration กับ API เพื่อน ──────────────────────

@app.get("/friend/tasks")
@jwt_required()
def get_friend_tasks():
    # login ด้วย service account ของเราที่เพื่อนรู้จัก
    try:
        login_resp = req.post(
            f"{FRIEND_BASE_URL}/login",
            json={"username": "student", "password": "HeyYoMyfriend"},
            timeout=(3, 30),
        )
    except req.RequestException as e:
        return jsonify({"msg": f"Cannot reach friend API: {e}"}), 500

    if login_resp.status_code != 200:
        return jsonify({"msg": "Login to friend API failed"}), login_resp.status_code

    friend_token = login_resp.json().get("token")
    headers = {"Authorization": f"Bearer {friend_token}"}

    try:
        tasks_resp = req.get(
            f"{FRIEND_BASE_URL}/tasks",
            headers=headers,
            timeout=(3, 30),
        )
    except req.RequestException as e:
        return jsonify({"msg": f"Cannot reach friend API: {e}"}), 500

    return jsonify(tasks_resp.json()), tasks_resp.status_code


@app.post("/friend/tasks")
@jwt_required()
def create_friend_task():
    # login ด้วย service account ของเราที่เพื่อนรู้จัก
    try:
        login_resp = req.post(
            f"{FRIEND_BASE_URL}/login",
            json={"username": "student", "password": "HeyYoMyfriend"},
            timeout=(3, 30),
        )
    except req.RequestException as e:
        return jsonify({"msg": f"Cannot reach friend API: {e}"}), 500

    if login_resp.status_code != 200:
        return jsonify({"msg": "Login to friend API failed"}), login_resp.status_code

    friend_token = login_resp.json().get("token")
    headers = {"Authorization": f"Bearer {friend_token}"}
    
    data = request.get_json() or {}

    try:
        tasks_resp = req.post(
            f"{FRIEND_BASE_URL}/tasks",
            headers=headers,
            json=data,
            timeout=(3, 30),
        )
    except req.RequestException as e:
        return jsonify({"msg": f"Cannot reach friend API: {e}"}), 500

    try:
        resp_data = tasks_resp.json()
    except ValueError:
        resp_data = {"msg": tasks_resp.text}

    return jsonify(resp_data), tasks_resp.status_code


# ─── Run ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)