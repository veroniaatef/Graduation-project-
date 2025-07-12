import sqlite3
import json
from datetime import datetime

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("interview_app.db", check_same_thread=False)
    return conn

# Initialize database
def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    
    # Create softskill_interviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS softskill_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            results TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    
    # Create conceptual_interviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conceptual_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            results TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    
    # Create coding_interviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coding_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            results TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    
    # Create complete_interviews table to track full interview sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complete_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            softskill_id INTEGER,
            conceptual_id INTEGER,
            coding_id INTEGER,
            FOREIGN KEY (username) REFERENCES users (username),
            FOREIGN KEY (softskill_id) REFERENCES softskill_interviews (id),
            FOREIGN KEY (conceptual_id) REFERENCES conceptual_interviews (id),
            FOREIGN KEY (coding_id) REFERENCES coding_interviews (id)
        )
    """)
    
    conn.commit()
    conn.close()

# Save softskill interview results
def save_softskill_results(username, results):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results_json = json.dumps(results)
        
        cursor.execute(
            "INSERT INTO softskill_interviews (username, date, results) VALUES (?, ?, ?)",
            (username, date, results_json)
        )
        conn.commit()
        
        # Get the inserted interview ID
        interview_id = cursor.lastrowid
        conn.close()
        
        return interview_id
    except Exception as e:
        print(f"Error saving softskill interview results: {str(e)}")
        return None

# Save conceptual interview results
def save_conceptual_results(username, results):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results_json = json.dumps(results)
        
        cursor.execute(
            "INSERT INTO conceptual_interviews (username, date, results) VALUES (?, ?, ?)",
            (username, date, results_json)
        )
        conn.commit()
        
        # Get the inserted interview ID
        interview_id = cursor.lastrowid
        conn.close()
        
        return interview_id
    except Exception as e:
        print(f"Error saving conceptual interview results: {str(e)}")
        return None

# Save coding interview results
def save_coding_results(username, results):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results_json = json.dumps(results)
        
        cursor.execute(
            "INSERT INTO coding_interviews (username, date, results) VALUES (?, ?, ?)",
            (username, date, results_json)
        )
        conn.commit()
        
        # Get the inserted interview ID
        interview_id = cursor.lastrowid
        conn.close()
        
        return interview_id
    except Exception as e:
        print(f"Error saving coding interview results: {str(e)}")
        return None

# Save complete interview session
def save_complete_interview(username, softskill_id, conceptual_id, coding_id=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO complete_interviews (username, date, softskill_id, conceptual_id, coding_id) VALUES (?, ?, ?, ?, ?)",
            (username, date, softskill_id, conceptual_id, coding_id)
        )
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error saving complete interview: {str(e)}")
        return False

# Get user's softskill interviews
def get_user_softskill_interviews(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, date, results FROM softskill_interviews WHERE username = ? ORDER BY date DESC",
            (username,)
        )
        interviews = []
        rows = cursor.fetchall()
        
        for row in rows:
            interview_id, date, results_json = row
            try:
                results_data = json.loads(results_json)
                interviews.append({
                    "id": interview_id,
                    "date": date,
                    "results": results_data
                })
            except json.JSONDecodeError:
                continue
                
        conn.close()
        return interviews
    except Exception as e:
        print(f"Error retrieving softskill interviews: {str(e)}")
        return []

# Get user's conceptual interviews
def get_user_conceptual_interviews(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, date, results FROM conceptual_interviews WHERE username = ? ORDER BY date DESC",
            (username,)
        )
        interviews = []
        rows = cursor.fetchall()
        
        for row in rows:
            interview_id, date, results_json = row
            try:
                results_data = json.loads(results_json)
                interviews.append({
                    "id": interview_id,
                    "date": date,
                    "results": results_data
                })
            except json.JSONDecodeError:
                continue
                
        conn.close()
        return interviews
    except Exception as e:
        print(f"Error retrieving conceptual interviews: {str(e)}")
        return []

# Get user's coding interviews
def get_user_coding_interviews(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, date, results FROM coding_interviews WHERE username = ? ORDER BY date DESC",
            (username,)
        )
        interviews = []
        rows = cursor.fetchall()
        
        for row in rows:
            interview_id, date, results_json = row
            try:
                results_data = json.loads(results_json)
                interviews.append({
                    "id": interview_id,
                    "date": date,
                    "results": results_data
                })
            except json.JSONDecodeError:
                continue
                
        conn.close()
        return interviews
    except Exception as e:
        print(f"Error retrieving coding interviews: {str(e)}")
        return []

# Get user's complete interviews
def get_user_complete_interviews(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ci.id, ci.date, 
                   si.id, si.results, 
                   ci2.id, ci2.results,
                   ci3.id, ci3.results
            FROM complete_interviews ci
            JOIN softskill_interviews si ON ci.softskill_id = si.id
            JOIN conceptual_interviews ci2 ON ci.conceptual_id = ci2.id
            LEFT JOIN coding_interviews ci3 ON ci.coding_id = ci3.id
            WHERE ci.username = ?
            ORDER BY ci.date DESC
        """, (username,))
        
        interviews = []
        rows = cursor.fetchall()
        
        for row in rows:
            complete_id, date, softskill_id, softskill_results_json, conceptual_id, conceptual_results_json, coding_id, coding_results_json = row
            try:
                softskill_data = json.loads(softskill_results_json)
                conceptual_data = json.loads(conceptual_results_json)
                
                interview_data = {
                    "id": complete_id,
                    "date": date,
                    "softskill": {
                        "id": softskill_id,
                        "results": softskill_data
                    },
                    "conceptual": {
                        "id": conceptual_id,
                        "results": conceptual_data
                    }
                }
                
                # Add coding data if available
                if coding_id and coding_results_json:
                    coding_data = json.loads(coding_results_json)
                    interview_data["coding"] = {
                        "id": coding_id,
                        "results": coding_data
                    }
                
                interviews.append(interview_data)
            except json.JSONDecodeError:
                continue
                
        conn.close()
        return interviews
    except Exception as e:
        print(f"Error retrieving complete interviews: {str(e)}")
        return []
