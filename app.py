from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client
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

# ------------------- Supabase Config -------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------- Helper Functions -------------------
def fetch_tasks():
    response = supabase.table('tasks').select('*').order('id', desc=True).execute()
    return response.data

def insert_task(description, due_date=None):
    data = {
        "description": description,
        "due_date": due_date
    }
    response = supabase.table('tasks').insert(data).execute()
    return response.data[0] if response.data else None

def update_task_completed(task_id):
    response = supabase.table('tasks').update({"completed": True}).eq('id', task_id).execute()
    return response.data[0] if response.data else None

def delete_task_by_id(task_id):
    response = supabase.table('tasks').delete().eq('id', task_id).execute()
    return response.data[0] if response.data else None

def complete_all_tasks():
    supabase.table('tasks').update({"completed": True}).neq('id', 0).execute()

def delete_all_tasks():
    supabase.table('tasks').delete().neq('id', 0).execute()

def add_random_tasks(count=10):
    """Add random sample tasks for testing/demo purposes"""
    sample_tasks = [
        {"description": "Buy groceries for the week", "due_date": None},
        {"description": "Complete project documentation", "due_date": None},
        {"description": "Schedule dentist appointment", "due_date": None},
        {"description": "Call mom to catch up", "due_date": None},
        {"description": "Prepare presentation slides", "due_date": None},
        {"description": "Review and respond to emails", "due_date": None},
        {"description": "Exercise for 30 minutes", "due_date": None},
        {"description": "Read chapter 5 of the book", "due_date": None},
        {"description": "Clean and organize workspace", "due_date": None},
        {"description": "Update resume and LinkedIn profile", "due_date": None},
        {"description": "Pay monthly bills", "due_date": None},
        {"description": "Plan weekend trip", "due_date": None},
        {"description": "Water the plants", "due_date": None},
        {"description": "Backup important files", "due_date": None},
        {"description": "Learn a new programming concept", "due_date": None},
        {"description": "Cook a healthy meal", "due_date": None},
        {"description": "Fix the leaking faucet", "due_date": None},
        {"description": "Sort through old photos", "due_date": None},
        {"description": "Meditate for 10 minutes", "due_date": None},
        {"description": "Write in journal", "due_date": None},
    ]
    
    # Randomly select tasks
    import random as rand
    selected_tasks = rand.sample(sample_tasks, min(count, len(sample_tasks)))
    
    # Insert tasks
    added_tasks = []
    for task_data in selected_tasks:
        response = supabase.table('tasks').insert(task_data).execute()
        if response.data:
            added_tasks.extend(response.data)
    
    return added_tasks

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
    supabase.table('tasks').update({"due_date": due_time}).eq('id', task_id).execute()
    return jsonify({"message": "Date updated"})


@app.route("/tasks/delete_all", methods=["DELETE"])
def delete_all():
    delete_all_tasks()
    return jsonify({"message": "All tasks deleted"}), 200

@app.route("/tasks/add_random", methods=["POST"])
def add_random():
    """Add 10 random tasks for testing/demo"""
    data = request.get_json() or {}
    count = data.get("count", 10)
    tasks = add_random_tasks(count)
    return jsonify({
        "message": f"Added {len(tasks)} random tasks",
        "tasks": tasks
    }), 201

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
   - addRandomTasks: {{"command": "addRandomTasks", "count": 10}}
- For casual chat, just reply normally without JSON.
User: "{user_text}"
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
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

                elif command == "addRandomTasks":
                    count = command_data.get("count", 10)
                    tasks = add_random_tasks(count)
                    return jsonify({
                        "ai_response": f"🎲 Added {len(tasks)} random tasks for testing!",
                        "tasks": tasks
                    }), 200

            except Exception as e:
                return jsonify({"ai_response": f"⚠️ JSON parse error: {str(e)}"}), 200

        # If no JSON, treat as casual chat
        return jsonify({"ai_response": ai_message}), 200

    except Exception as e:
        return jsonify({"ai_response": f"⚠️ AI error: {str(e)}"}), 200

# ------------------- Run -------------------
if __name__ == "__main__":
    app.run(debug=True)
