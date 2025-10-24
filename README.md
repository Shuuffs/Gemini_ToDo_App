# 📝 AI To-Do List App

A smart to-do list powered by Google's Gemini AI and Supabase cloud database.

---

## 🚀 Quick Setup Guide

### Step 1: Get Your API Keys

#### **Gemini API Key** (for AI chatbot)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### **Supabase Credentials** (for cloud database)
1. Go to https://supabase.com (sign up for free)
2. Create a new project
3. Go to **Settings** → **API**
4. Copy these two things:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (long string of letters/numbers)

---

### Step 2: Install Dependencies

Open your terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

This installs Flask, Supabase, Gemini, and other required packages.

---

### Step 3: Configure Environment Variables

Create a file named `.env` in the project folder and add:

```env
GEMINI_API_KEY=paste_your_gemini_key_here
SUPABASE_URL=paste_your_supabase_url_here
SUPABASE_KEY=paste_your_supabase_anon_key_here
```

**Replace** the values with your actual keys from Step 1.

---

### Step 4: Create Database Table

1. Open your Supabase dashboard
2. Go to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy and paste this SQL:

```sql
CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all operations for everyone" 
  ON tasks 
  FOR ALL 
  USING (true);
```

5. Click **Run** (or press `Ctrl+Enter`)
6. You should see "Success. No rows returned"

---

### Step 5: Test Connection

Run this test script to verify everything works:

```bash
python init_supabase.py
```

**Expected output:**
```
✅ Supabase client initialized successfully!
✅ Successfully connected to 'tasks' table!
```

---

### Step 6: Run the App

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## 🎉 You're Done!

### How to Use:

**Add tasks manually:**
- Type in the text box at the bottom
- Optionally select a due date
- Click "Add Task"

**Chat with AI:**
- Type in the AI Assistant panel
- Try: "Add a task to buy groceries tomorrow"
- Or: "Add 10 random tasks"
- Or just chat casually!

**Manage tasks:**
- Click ✅ to mark as complete
- Click 🗑️ to delete
- Use search, filter, and sort options

---

## ❓ Troubleshooting

**"SUPABASE_URL and SUPABASE_KEY must be set"**
- Make sure your `.env` file is in the correct folder
- Check that variable names are exactly: `SUPABASE_URL` and `SUPABASE_KEY`
- Make sure there are no spaces around the `=` sign

**"relation 'tasks' does not exist"**
- Go back to Step 4 and run the SQL in Supabase SQL Editor
- Make sure you clicked "Run" and saw a success message

**"new row violates row-level security policy"**
- Run the SQL policy from Step 4 again (the `CREATE POLICY` part)

**AI not responding**
- Check your `GEMINI_API_KEY` is correct in `.env`
- Make sure you have internet connection
- Try restarting the Flask app

---

## 📁 Project Files

```
Gemini_ToDo_App/
├── app.py                 # Main Flask backend
├── requirements.txt       # Python packages
├── init_supabase.py      # Connection test script
├── init_supabase.sql     # Database schema
├── .env                  # Your API keys (create this!)
├── templates/
│   └── index.html        # Frontend UI
└── static/
    └── style.css         # Styling
```

---

## 🔧 Tech Stack

- **Backend:** Flask (Python)
- **Database:** Supabase (PostgreSQL)
- **AI:** Google Gemini 2.5 Flash
- **Frontend:** HTML, CSS, JavaScript

---

## 💡 Tips

- Keep your `.env` file private - never share it!
- The app uses your Supabase free tier (no credit card needed)
- Gemini API has a free tier too
- Tasks are stored in the cloud, accessible from anywhere

---

## 🆘 Need More Help?

- Check `init_supabase.sql` for the database schema
- Check `env.template` for environment variable format
- Supabase docs: https://supabase.com/docs
- Gemini API docs: https://ai.google.dev/docs

---

Made with ❤️ using Gemini AI and Supabase
