"""
Supabase Connection Test & Setup Script

This script verifies your Supabase connection and checks if the tasks table exists.
Run this after creating your table in the Supabase dashboard.

Usage:
    python init_supabase.py
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    """Test Supabase connection and verify table exists"""
    
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Check if credentials are set
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        print("\nAdd these lines to your .env file:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_KEY=your_supabase_anon_key")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully!")
        
        # Test connection by querying the tasks table
        response = supabase.table('tasks').select('*').limit(1).execute()
        print("✅ Successfully connected to 'tasks' table!")
        print(f"📊 Current number of tasks: {len(response.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        print("\n⚠️  Make sure you have:")
        print("   1. Created the 'tasks' table in Supabase dashboard")
        print("   2. Run the SQL schema from init_supabase.sql")
        print("   3. Set correct SUPABASE_URL and SUPABASE_KEY in .env")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Supabase Connection Test")
    print("=" * 50)
    print()
    
    success = test_supabase_connection()
    
    print()
    if success:
        print("🎉 Setup complete! You can now run: python app.py")
    else:
        print("📝 Follow the instructions above to fix the connection")
    print("=" * 50)

