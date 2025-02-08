import sqlite3
from datetime import datetime
import os
import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import hashlib

def create_connection():
    """Create a connection to the database"""
    db_path = './Code_app/hospital.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON") 
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_database():
    """Create and initialize the database"""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            
            # Users table
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL, 
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Patients table
            c.execute('''CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT,
                gender TEXT,
                id_number TEXT UNIQUE,
                address TEXT,
                phone TEXT UNIQUE,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Diagnoses table
            c.execute('''CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                doctor TEXT,
                image_path TEXT,
                processed_image_path TEXT,
                detection_result TEXT,
                classification_result TEXT, 
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
            )''')

            # Add default accounts
            default_users = [
                ('admin', 'admin123', 'admin'),
                ('doctor', 'doctor123', 'doctor')
            ]
            
            for username, password, role in default_users:
                c.execute("""
                    INSERT OR IGNORE INTO users 
                    (username, password, role) 
                    VALUES (?, ?, ?)
                """, (username, password, role))

            conn.commit()
            print("Database created successfully")
            
        except sqlite3.Error as e:
            print(f"Database creation error: {e}")
            conn.rollback()
        finally:
            conn.close()

def check_login(username, password):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            # Lấy stored password từ database
            c.execute("SELECT password, role FROM users WHERE username=?", (username,))
            result = c.fetchone()
            
            if result:
                stored_password, role = result
                salt = stored_password.split(':')[0]
                hashed = hashlib.sha256((password + salt).encode()).hexdigest()
                
                if f"{salt}:{hashed}" == stored_password:
                    return role
            return None
        except sqlite3.Error as e:
            print(f"Login verification error: {e}")
            return None
        finally:
            conn.close()

def reset_database():
    """Delete and recreate the database"""
    try:
        db_path = './Code_app/hospital.db'
        if os.path.exists(db_path):
            os.remove(db_path)
        create_database()
        return True
    except Exception as e:
        print(f"Database reset error: {e}")
        return False

def backup_database(window):
    """Backup the database"""
    try:
        backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename, _ = QFileDialog.getSaveFileName(
            window, 
            "Save Backup", 
            f"backup_{backup_time}.db", 
            "Database Files (*.db)"
        )
        
        if filename:
            conn = create_connection()
            with open(filename, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            
            QMessageBox.information(window, 'Success', 'Data backup completed!')
            return True
    except Exception as e:
        QMessageBox.critical(window, 'Error', f'Cannot backup: {str(e)}')
        return False

def restore_database(window):
    """Restore database from backup file"""
    conn = None
    try:
        filename, _ = QFileDialog.getOpenFileName(
            window,
            "Select Backup File",
            window.backup_dir,
            "Database Files (*.db)"
        )
        
        if filename:
            conn = create_connection()
            conn.executescript('')  
            
            with open(filename, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            
            conn.commit()
            window.load_data()  
            
            QMessageBox.information(window, 'Success', 'Data restored successfully!')
            return True
    except Exception as e:
        if conn:
            conn.rollback()
        QMessageBox.critical(window, 'Error', f'Cannot restore: {str(e)}')
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()