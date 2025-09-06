from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import google.generativeai as genai
import re, json, random
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

# ------------------- Load Gemini -------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ------------------- Database Config -------------------
DB_CONFIG = {
    "dbname": "todos_db",
    "user": "postgres",
    "password": 1507,   # change if needed
    "host": "localhost",
    "port": 5432
}

# ------------------- Helper Functions -------------------
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def fetch_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id DESC;")
            return cur.fetchall()

def insert_task(description, due_date=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (description, due_date) VALUES (%s, %s) RETURNING *;",
                (description, due_date)
            )
            return cur.fetchone()

def update_task_completed(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET completed = TRUE WHERE id = %s RETURNING *;",
                (task_id,)
            )
            return cur.fetchone()

def delete_task_by_id(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING *;", (task_id,))
            return cur.fetchone()

def complete_all_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET completed = TRUE;")

def delete_all_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks;")

# ------------------- Routes -------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = fetch_tasks()
    return jsonify(tasks), 200

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or "description" not in data:
        return jsonify({"error": "Task description is required"}), 400
    task = insert_task(data["description"], data.get("due_time"))
    return jsonify(task), 201

@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    task = update_task_completed(task_id)
    if task:
        return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = delete_task_by_id(task_id)
    if task:
        return jsonify({"message": "Task deleted"}), 200
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/complete_all", methods=["PUT"])
def complete_all():
    complete_all_tasks()
    return jsonify({"message": "All tasks completed"}), 200

@app.route("/tasks/<int:task_id>/date", methods=["PUT"])
def update_date(task_id):
    data = request.get_json()
    due_time = data.get("due_time")
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET due_date=%s WHERE id=%s", (due_time, task_id))
            conn.commit()
    return jsonify({"message": "Date updated"})


@app.route("/tasks/delete_all", methods=["DELETE"])
def delete_all():
    delete_all_tasks()
    return jsonify({"message": "All tasks deleted"}), 200

# ------------------- AI Endpoint -------------------
@app.route("/ai", methods=["POST"])
def ai_command():
    user_text = request.json.get("user_text", "")
    if not user_text:
        return jsonify({"error": "No user text provided"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"ai_response": "⚠️ Gemini unavailable, add tasks manually."}), 200

    system_prompt = f"""
You are Hanni, a helpful AI assistant for a To-Do List app.

Rules:
- Always output valid JSON for commands (inside triple backticks).
- If the user specifies a due date, use it exactly as provided (YYYY-MM-DD).
- Only generate a random due date if the user did not specify one.
- Commands:
   - addTask: {{"command": "addTask", "tasks": [{{"description": "...", "due_time": null}}]}}
   - completeTask: {{"command": "completeTask", "task_id": number}}
   - completeAllTasks: {{"command": "completeAllTasks"}}
   - deleteTask: {{"command": "deleteTask", "task_id": number}}
   - deleteAllTasks: {{"command": "deleteAllTasks"}}
   - viewTasks: {{"command": "viewTasks"}}
- For casual chat, just reply normally without JSON.
User: "{user_text}"
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(system_prompt)
        ai_message = response.text.strip()

        # Extract JSON block from AI response
        match = re.search(r"```json(.*?)```", ai_message, re.DOTALL)
        if match:
            try:
                command_data = json.loads(match.group(1).strip())
                command = command_data.get("command")

                if command == "addTask":
                    tasks_added = []
                    for t in command_data.get("tasks", []):
                        task = insert_task(t["description"], t.get("due_time"))
                        tasks_added.append(task)

                    # Build a message showing task names and actual due dates
                    msg_list = []
                    for task in tasks_added:
                        due = f" (Due: {task['due_date']})" if task['due_date'] else ""
                        msg_list.append(f"{task['description']}{due}")

                    return jsonify({
                        "ai_response": f"✅ Added {len(tasks_added)} task(s): " + ", ".join(msg_list),
                        "tasks": tasks_added
                    }), 200

                elif command == "completeTask":
                    task_id = command_data.get("task_id")
                    if task_id:
                        task = update_task_completed(task_id)
                        if task:
                            return jsonify({"ai_response": f"✅ Completed task {task_id}."}), 200
                        else:
                            return jsonify({"ai_response": f"⚠️ Task {task_id} not found."}), 404

                elif command == "completeAllTasks":
                    complete_all_tasks()
                    return jsonify({"ai_response": "✅ All tasks completed."}), 200

                elif command == "deleteTask":
                    task_id = command_data.get("task_id")
                    if task_id:
                        task = delete_task_by_id(task_id)
                        if task:
                            return jsonify({"ai_response": f"🗑️ Deleted task {task_id}."}), 200
                        else:
                            return jsonify({"ai_response": f"⚠️ Task {task_id} not found."}), 404

                elif command == "deleteAllTasks":
                    delete_all_tasks()
                    return jsonify({"ai_response": "🗑️ All tasks deleted."}), 200

                elif command == "viewTasks":
                    tasks = fetch_tasks()
                    return jsonify({"ai_response": "📋 Your tasks:", "tasks": tasks}), 200

            except Exception as e:
                return jsonify({"ai_response": f"⚠️ JSON parse error: {str(e)}"}), 200

        # If no JSON, treat as casual chat
        return jsonify({"ai_response": ai_message}), 200

    except Exception as e:
        return jsonify({"ai_response": f"⚠️ AI error: {str(e)}"}), 200

# ------------------- Run -------------------
if __name__ == "__main__":
    app.run(debug=True)
