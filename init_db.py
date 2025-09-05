import psycopg2

DB_CONFIG = {
    "dbname": "todos_db",
    "user": "postgres",
    "password": 1507,
    "host": "localhost",
    "port": 5432
}


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    due_date DATE
);
"""

def init_db():
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_SQL)
                conn.commit()
        print("✅ tasks table created successfully!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    init_db()
