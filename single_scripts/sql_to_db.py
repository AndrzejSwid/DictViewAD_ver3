import os
import sqlite3

# Path to your SQL file
sql_file_path = "tatoeba2_jmdict_withjlpt_english_only.sql"

# Path to your SQLite database (or ':memory:' to use an in-memory database)
sqlite_db_path = "temp.sqlite3"

# Get current file path
current_file_path = os.path.abspath(__file__)

# Construct the full file paths
sql_file_path = os.path.join(os.path.dirname(current_file_path), sql_file_path)
sqlite_db_path = os.path.join(os.path.dirname(current_file_path), sqlite_db_path)

# Read the SQL file
with open(sql_file_path, "r", encoding="utf-8") as file:
    sql_script = file.read()

# Connect to the SQLite database
conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

# Execute the SQL script
try:
    cursor.executescript(sql_script)
    print("SQL script executed successfully!")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
