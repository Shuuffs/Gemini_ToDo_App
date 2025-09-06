Setup Guide: Gemini To-Do App
1. Clone the Repository
git clone https://github.com/Shuuffs/Gemini_ToDo_App.git
cd Gemini_ToDo_App

2. Install Dependencies

Make sure you have Python 3.10+ installed.

Install required Python packages:

pip install -r requirements.txt

3. Create Environment Variables

In the project root, create a .env file:

GEMINI_API_KEY=MASUKAN_SINI


Replace MASUKAN_SINI with your actual Gemini API key.

The .env file is used by the backend to authenticate with Gemini API.

4. Set Up PostgreSQL Database

Make sure PostgreSQL is installed and running.

Open your PostgreSQL shell (psql) or use a database GUI tool, and create the database:

CREATE DATABASE todos_db;

5. Initialize the Database Table

Run the init_db.py script to create the tasks table:

python init_db.py


Expected output:

✅ tasks table created successfully!

6. Run the Backend

Start the Flask backend:

python app.py


This will serve your API on http://127.0.0.1:5000/ (default).

7. Run the Frontend

Open index.html in a browser.

Ensure the backend is running so the frontend can fetch and update tasks.

8. Features Verified

Add tasks (with or without due dates).

Complete or delete tasks.

Tasks persist after backend restart.

AI Assistant can handle natural-language task addition using the Gemini API.

9. Optional Enhancements

Refresh Button for Task Manager:
Add a Refresh button on the task panel for manual refresh.

Date Formatting:
Use toLocaleDateString in JS for human-readable dates: 10 Oct 2025.

10. Notes

Ensure .env is never committed to GitHub. Add it to .gitignore.

Backend automatically reads GEMINI_API_KEY
