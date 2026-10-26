"""
Campus Connect - Database Layer
Handles SQLite database connection, table initialization, and CRUD operations
for College Issues & Complaints Management System.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_connect.db")

def get_connection():
    """Return a connection to the SQLite database with dictionary cursor."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables and create default seed data if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        location TEXT NOT NULL,
        student_name TEXT NOT NULL,
        roll_no TEXT NOT NULL,
        department TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open',
        admin_notes TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    conn.commit()

    # Check if empty, then seed sample data
    cursor.execute("SELECT COUNT(*) as count FROM complaints")
    row = cursor.fetchone()
    if row["count"] == 0:
        seed_sample_data(conn)
        
    conn.close()

def generate_ticket_id(cursor) -> str:
    """Generate human-readable ticket ID like CC-1001."""
    cursor.execute("SELECT MAX(id) as max_id FROM complaints")
    row = cursor.fetchone()
    next_num = (row["max_id"] or 0) + 1
    return f"CC-{1000 + next_num}"

def seed_sample_data(conn):
    """Seed initial realistic college complaints."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    samples = [
        (
            "CC-1001",
            "Wi-Fi Connectivity Down in Hostel Block B",
            "Infrastructure & IT",
            "High",
            "Hostel Block B, 3rd Floor",
            "Aarav Sharma",
            "2023CS101",
            "Computer Science",
            "aarav.sharma@college.edu",
            "9876543210",
            "The Wi-Fi access points on the 3rd floor of Hostel B have been disconnecting frequently since yesterday.",
            "In Progress",
            "IT department engineer dispatched to check the switch router.",
            now,
            now
        ),
        (
            "CC-1002",
            "Projector Display Flickering in LH-204",
            "Academic & Classroom",
            "Medium",
            "Lecture Hall 204",
            "Priya Patel",
            "2022EC045",
            "Electronics & Comm",
            "priya.patel@college.edu",
            "9811223344",
            "The HDMI connection cable and projector lamp flicker during morning lectures.",
            "Open",
            "",
            now,
            now
        ),
        (
            "CC-1003",
            "Water Cooler Not Cooling near Central Library",
            "Campus Facilities",
            "Low",
            "Central Library 1st Floor",
            "Rohan Verma",
            "2024ME089",
            "Mechanical",
            "rohan.v@college.edu",
            "9988776655",
            "The RO water dispenser is delivering warm water instead of cool filtered water.",
            "Resolved",
            "Compressor filter serviced and cooling thermostat replaced by estate team.",
            now,
            now
        ),
        (
            "CC-1004",
            "Library Fee Receipt Mismatch in Portal",
            "Admin & Accounts",
            "Medium",
            "Admin Block Window 4",
            "Sneha Kulkarni",
            "2021IT023",
            "Information Tech",
            "sneha.k@college.edu",
            "9765432109",
            "Payment made on 15th Oct for semester book deposit shows pending on ERP portal.",
            "Open",
            "",
            now,
            now
        ),
        (
            "CC-1005",
            "Mess Dinner Food Quality & Hygiene Feedback",
            "Hostel & Mess",
            "Urgent",
            "North Dining Hall",
            "Vikram Singh",
            "2023CE064",
            "Civil Engineering",
            "vikram.s@college.edu",
            "9123456780",
            "Food served last night was undercooked and water dispenser cups were exhausted.",
            "In Progress",
            "Hostel warden inspected dining hall and issued warning to catering vendor.",
            now,
            now
        )
    ]
    
    cursor = conn.cursor()
    cursor.executemany("""
    INSERT INTO complaints (
        ticket_id, title, category, priority, location,
        student_name, roll_no, department, email, phone,
        description, status, admin_notes, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, samples)
    conn.commit()

def create_complaint(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new complaint record."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket_id = generate_ticket_id(cursor)
    
    cursor.execute("""
    INSERT INTO complaints (
        ticket_id, title, category, priority, location,
        student_name, roll_no, department, email, phone,
        description, status, admin_notes, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        data.get("title", "").strip(),
        data.get("category", "General"),
        data.get("priority", "Medium"),
        data.get("location", "").strip(),
        data.get("student_name", "").strip(),
        data.get("roll_no", "").strip().upper(),
        data.get("department", "").strip(),
        data.get("email", "").strip(),
        data.get("phone", "").strip(),
        data.get("description", "").strip(),
        data.get("status", "Open"),
        data.get("admin_notes", ""),
        now,
        now
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_complaint_by_id(new_id)

def get_all_complaints(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieve complaints with optional filtering and search."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM complaints WHERE 1=1"
    params = []
    
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
        
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
        
    if priority and priority != "All":
        query += " AND priority = ?"
        params.append(priority)
        
    if search:
        search_like = f"%{search.strip()}%"
        query += " AND (ticket_id LIKE ? OR title LIKE ? OR roll_no LIKE ? OR student_name LIKE ? OR location LIKE ?)"
        params.extend([search_like, search_like, search_like, search_like, search_like])
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results

def get_complaint_by_id(complaint_id: int) -> Optional[Dict[str, Any]]:
    """Get single complaint by its primary key ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_complaint_by_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Get single complaint by its Ticket ID (e.g. CC-1001)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_complaint(complaint_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update fields of an existing complaint."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    fields = []
    values = []
    allowed = ["title", "category", "priority", "location", "status", "admin_notes", "department", "email", "phone", "description"]
    for key, val in updates.items():
        if key in allowed and val is not None:
            fields.append(f"{key} = ?")
            values.append(val)
            
    if not fields:
        conn.close()
        return get_complaint_by_id(complaint_id)
        
    fields.append("updated_at = ?")
    values.append(now)
    values.append(complaint_id)
    
    sql = f"UPDATE complaints SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return get_complaint_by_id(complaint_id)

def delete_complaint(complaint_id: int) -> bool:
    """Delete a complaint by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def get_statistics() -> Dict[str, Any]:
    """Calculate summary statistics for college dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM complaints")
    total = cursor.fetchone()["total"]
    
    cursor.execute("SELECT status, COUNT(*) as count FROM complaints GROUP BY status")
    by_status = {row["status"]: row["count"] for row in cursor.fetchall()}
    
    cursor.execute("SELECT category, COUNT(*) as count FROM complaints GROUP BY category")
    by_category = {row["category"]: row["count"] for row in cursor.fetchall()}
    
    cursor.execute("SELECT priority, COUNT(*) as count FROM complaints GROUP BY priority")
    by_priority = {row["priority"]: row["count"] for row in cursor.fetchall()}
    
    conn.close()
    return {
        "total": total,
        "open": by_status.get("Open", 0),
        "in_progress": by_status.get("In Progress", 0),
        "resolved": by_status.get("Resolved", 0),
        "by_status": by_status,
        "by_category": by_category,
        "by_priority": by_priority
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    print(f"Stats: {get_statistics()}")
