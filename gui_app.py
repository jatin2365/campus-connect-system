"""
Campus Connect - PySimpleGUI Desktop Application
UI for students and college administration to submit, track, update,
and manage campus complaints and issues.
Communicates with FastAPI backend REST API with seamless local database fallback.
"""

import sys
import os
import csv
import json
import threading
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import FreeSimpleGUI as sg
except ImportError:
    try:
        import PySimpleGUI as sg
    except ImportError:
        print("Please install FreeSimpleGUI: pip install FreeSimpleGUI")
        sys.exit(1)

import requests
import database

API_BASE_URL = "http://127.0.0.1:8000"

CATEGORIES = [
    "All",
    "Infrastructure & IT",
    "Academic & Classroom",
    "Hostel & Mess",
    "Campus Facilities",
    "Admin & Accounts",
    "Security & Transport",
    "General"
]

SUBMIT_CATEGORIES = [c for c in CATEGORIES if c != "All"]

DEPARTMENTS = [
    "Computer Science",
    "Information Tech",
    "Electronics & Comm",
    "Electrical & Electronics",
    "Mechanical Engineering",
    "Civil Engineering",
    "Biotechnology",
    "Management & MBA",
    "Basic Sciences"
]

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Open", "In Progress", "Resolved"]

# Helper functions to query API or fallback to DB
def check_api_status() -> bool:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/health", timeout=1.5)
        return resp.status_code == 200
    except Exception:
        return False

def api_get_complaints(status="All", category="All", priority="All", search=""):
    try:
        params = {}
        if status and status != "All":
            params["status"] = status
        if category and category != "All":
            params["category"] = category
        if priority and priority != "All":
            params["priority"] = priority
        if search and search.strip():
            params["search"] = search.strip()
        
        resp = requests.get(f"{API_BASE_URL}/api/complaints", params=params, timeout=2.0)
        if resp.status_code == 200:
            return resp.json(), "API"
    except Exception:
        pass
    # Fallback to local DB
    return database.get_all_complaints(status=status, category=category, priority=priority, search=search), "DB"

def api_create_complaint(payload):
    try:
        resp = requests.post(f"{API_BASE_URL}/api/complaints", json=payload, timeout=2.0)
        if resp.status_code in (200, 201):
            return resp.json().get("complaint"), "API"
    except Exception:
        pass
    # Fallback to local DB
    return database.create_complaint(payload), "DB"

def api_update_complaint(complaint_id, updates):
    try:
        resp = requests.put(f"{API_BASE_URL}/api/complaints/{complaint_id}", json=updates, timeout=2.0)
        if resp.status_code == 200:
            return resp.json().get("complaint"), "API"
    except Exception:
        pass
    # Fallback to local DB
    return database.update_complaint(complaint_id, updates), "DB"

def api_delete_complaint(complaint_id):
    try:
        resp = requests.delete(f"{API_BASE_URL}/api/complaints/{complaint_id}", timeout=2.0)
        if resp.status_code == 200:
            return True, "API"
    except Exception:
        pass
    # Fallback to local DB
    return database.delete_complaint(complaint_id), "DB"

def api_get_stats():
    try:
        resp = requests.get(f"{API_BASE_URL}/api/stats", timeout=1.5)
        if resp.status_code == 200:
            return resp.json(), "API"
    except Exception:
        pass
    return database.get_statistics(), "DB"

def create_gui_app():
    # Set PySimpleGUI Theme
    sg.theme("DarkTeal9")
    sg.set_options(font=("Segoe UI", 10))

    # TABLE HEADERS
    table_headers = ["ID", "Ticket", "Date", "Student", "Roll No", "Dept", "Category", "Priority", "Status", "Location", "Title"]
    
    # TAB 1: LODGE COMPLAINT (Student / Staff submission)
    tab1_layout = [
        [sg.Text("Student & Complainant Information", font=("Segoe UI", 12, "bold"), text_color="#F4D03F")],
        [
            sg.Text("Full Name: *", size=(14, 1)),
            sg.Input(key="-NAME-", size=(28, 1)),
            sg.Text("Roll / Reg No: *", size=(14, 1)),
            sg.Input(key="-ROLL-", size=(25, 1))
        ],
        [
            sg.Text("Department: *", size=(14, 1)),
            sg.Combo(DEPARTMENTS, default_value=DEPARTMENTS[0], key="-DEPT-", size=(26, 1), readonly=True),
            sg.Text("Campus Location: *", size=(14, 1)),
            sg.Input(key="-LOCATION-", size=(25, 1), tooltip="e.g. Hostel B Room 204 or CS Lab 3")
        ],
        [
            sg.Text("Official Email: *", size=(14, 1)),
            sg.Input(key="-EMAIL-", size=(28, 1)),
            sg.Text("Phone Number:", size=(14, 1)),
            sg.Input(key="-PHONE-", size=(25, 1))
        ],
        [sg.HorizontalSeparator(pad=(0, 10))],
        [sg.Text("Issue & Complaint Classification", font=("Segoe UI", 12, "bold"), text_color="#F4D03F")],
        [
            sg.Text("Category: *", size=(14, 1)),
            sg.Combo(SUBMIT_CATEGORIES, default_value=SUBMIT_CATEGORIES[0], key="-CAT-", size=(26, 1), readonly=True),
            sg.Text("Urgency / Priority:", size=(14, 1)),
            sg.Combo(PRIORITIES, default_value="Medium", key="-PRIORITY-", size=(25, 1), readonly=True)
        ],
        [
            sg.Text("Issue Title: *", size=(14, 1)),
            sg.Input(key="-TITLE-", size=(71, 1), tooltip="Brief summary of the issue")
        ],
        [
            sg.Text("Full Description: *", size=(14, 1)),
            sg.Multiline(key="-DESC-", size=(71, 5), tooltip="Detailed description of the issue faced")
        ],
        [
            sg.Button("🚀 Submit Complaint", key="-SUBMIT-", size=(18, 1), button_color=("white", "#27AE60")),
            sg.Button("🧹 Reset Form", key="-CLEAR-", size=(14, 1), button_color=("white", "#7F8C8D")),
            sg.Text("", key="-SUBMIT-STATUS-", size=(50, 1), text_color="#2ECC71", font=("Segoe UI", 10, "bold"))
        ]
    ]

    # TAB 2: MANAGE & TRACK COMPLAINTS
    tab2_layout = [
        [
            sg.Text("Filter By: ", font=("Segoe UI", 10, "bold")),
            sg.Text("Status:"),
            sg.Combo(["All"] + STATUSES, default_value="All", key="-FILTER-STATUS-", size=(12, 1), readonly=True),
            sg.Text("Category:"),
            sg.Combo(CATEGORIES, default_value="All", key="-FILTER-CAT-", size=(18, 1), readonly=True),
            sg.Text("Priority:"),
            sg.Combo(["All"] + PRIORITIES, default_value="All", key="-FILTER-PRIORITY-", size=(10, 1), readonly=True),
            sg.Text("Search:"),
            sg.Input(key="-SEARCH-KEY-", size=(15, 1), tooltip="Search ticket, roll no, or title"),
            sg.Button("🔍 Filter", key="-APPLY-FILTER-", button_color=("white", "#2980B9")),
            sg.Button("🔄 Refresh", key="-REFRESH-TABLE-", button_color=("white", "#16A085"))
        ],
        [
            sg.Table(
                values=[],
                headings=table_headers,
                max_col_width=25,
                auto_size_columns=False,
                col_widths=[4, 8, 11, 14, 10, 14, 16, 8, 10, 16, 26],
                display_row_numbers=False,
                justification="left",
                num_rows=9,
                key="-TABLE-",
                selected_row_colors=("white", "#34495E"),
                enable_events=True,
                expand_x=True,
                alternating_row_color="#1E2A38"
            )
        ],
        [sg.Text("Selected Complaint & Admin Action Panel", font=("Segoe UI", 11, "bold"), text_color="#F4D03F")],
        [
            sg.Frame("Complaint Details", [
                [
                    sg.Text("Ticket ID:", size=(10, 1), font=("Segoe UI", 9, "bold")),
                    sg.Text("None selected", key="-SEL-TICKET-", size=(15, 1), text_color="#58D68D"),
                    sg.Text("Complainant:", size=(11, 1), font=("Segoe UI", 9, "bold")),
                    sg.Text("-", key="-SEL-STUDENT-", size=(25, 1)),
                    sg.Text("Roll No:", size=(8, 1), font=("Segoe UI", 9, "bold")),
                    sg.Text("-", key="-SEL-ROLL-", size=(15, 1))
                ],
                [
                    sg.Text("Location:", size=(10, 1), font=("Segoe UI", 9, "bold")),
                    sg.Text("-", key="-SEL-LOC-", size=(35, 1)),
                    sg.Text("Contact:", size=(8, 1), font=("Segoe UI", 9, "bold")),
                    sg.Text("-", key="-SEL-CONTACT-", size=(35, 1))
                ],
                [
                    sg.Text("Description:", size=(10, 1), font=("Segoe UI", 9, "bold")),
                    sg.Multiline("", key="-SEL-DESC-", size=(85, 3), disabled=True, no_scrollbar=False)
                ]
            ], expand_x=True)
        ],
        [
            sg.Frame("Admin Resolution & Status Update", [
                [
                    sg.Text("Update Status:", font=("Segoe UI", 9, "bold")),
                    sg.Combo(STATUSES, key="-UPDATE-STATUS-", size=(14, 1), readonly=True),
                    sg.Text("Update Priority:", font=("Segoe UI", 9, "bold")),
                    sg.Combo(PRIORITIES, key="-UPDATE-PRIORITY-", size=(12, 1), readonly=True),
                    sg.Button("💾 Save Update", key="-SAVE-UPDATE-", button_color=("white", "#27AE60")),
                    sg.Button("🗑️ Delete Ticket", key="-DELETE-TICKET-", button_color=("white", "#C0392B")),
                    sg.Button("📥 Export to CSV", key="-EXPORT-CSV-", button_color=("white", "#8E44AD")),
                    sg.Text("", key="-ACTION-MSG-", size=(25, 1), text_color="#F1C40F")
                ],
                [
                    sg.Text("Admin Notes / Resolution Action:", font=("Segoe UI", 9, "bold")),
                    sg.Input(key="-UPDATE-NOTES-", size=(70, 1), tooltip="Enter remarks, technician assigned, or fix applied")
                ]
            ], expand_x=True)
        ]
    ]

    # TAB 3: ANALYTICS & SYSTEM STATUS
    tab3_layout = [
        [sg.Text("College Campus Issues Metrics & System Health", font=("Segoe UI", 12, "bold"), text_color="#F4D03F")],
        [
            sg.Frame("Key Metrics", [
                [
                    sg.Text("Total Complaints:", size=(18, 1), font=("Segoe UI", 11)),
                    sg.Text("0", key="-STAT-TOTAL-", font=("Segoe UI", 13, "bold"), size=(8, 1), text_color="#3498DB"),
                    sg.Text("Open / Pending:", size=(16, 1), font=("Segoe UI", 11)),
                    sg.Text("0", key="-STAT-OPEN-", font=("Segoe UI", 13, "bold"), size=(8, 1), text_color="#E74C3C"),
                    sg.Text("In Progress:", size=(14, 1), font=("Segoe UI", 11)),
                    sg.Text("0", key="-STAT-INPROG-", font=("Segoe UI", 13, "bold"), size=(8, 1), text_color="#F39C12"),
                    sg.Text("Resolved:", size=(12, 1), font=("Segoe UI", 11)),
                    sg.Text("0", key="-STAT-RESOLVED-", font=("Segoe UI", 13, "bold"), size=(8, 1), text_color="#2ECC71")
                ]
            ], expand_x=True, pad=(0, 10))
        ],
        [
            sg.Frame("Complaints by Category", [
                [sg.Multiline(key="-CAT-BREAKDOWN-", size=(45, 8), disabled=True, font=("Consolas", 10))]
            ]),
            sg.Frame("Complaints by Priority", [
                [sg.Multiline(key="-PRIORITY-BREAKDOWN-", size=(45, 8), disabled=True, font=("Consolas", 10))]
            ])
        ],
        [sg.HorizontalSeparator(pad=(0, 10))],
        [
            sg.Frame("Backend & REST API Status", [
                [
                    sg.Text("API Endpoint:"),
                    sg.Input(API_BASE_URL, key="-API-URL-", size=(28, 1)),
                    sg.Button("⚡ Test Connection", key="-TEST-API-", button_color=("white", "#2980B9")),
                    sg.Text("Checking...", key="-API-STATUS-LABEL-", font=("Segoe UI", 10, "bold"), size=(30, 1))
                ],
                [
                    sg.Text("Interactive API Docs available at: http://127.0.0.1:8000/docs", text_color="#85C1E9", font=("Segoe UI", 9, "italic"))
                ]
            ], expand_x=True)
        ]
    ]

    # MAIN WINDOW LAYOUT
    header_layout = [
        [
            sg.Text("🏛️ CAMPUS CONNECT", font=("Segoe UI", 18, "bold"), text_color="#58D68D"),
            sg.Text("— College Issue & Complaint Management System", font=("Segoe UI", 13), text_color="#BDC3C7"),
            sg.Push(),
            sg.Text("Mode: Auto (API & Local DB)", key="-MODE-BADGE-", text_color="#F1C40F", font=("Segoe UI", 9, "bold"))
        ]
    ]

    layout = [
        header_layout,
        [sg.HorizontalSeparator(pad=(0, 5))],
        [
            sg.TabGroup([
                [
                    sg.Tab("📝 Lodge Complaint", tab1_layout),
                    sg.Tab("📋 Manage & Track Complaints", tab2_layout),
                    sg.Tab("📊 Analytics & System Status", tab3_layout)
                ]
            ], key="-TABS-", expand_x=True, expand_y=True)
        ],
        [
            sg.StatusBar("Ready. Campus Connect initialized.", key="-STATUSBAR-", size=(75, 1), relief=sg.RELIEF_SUNKEN)
        ]
    ]

    window = sg.Window(
        "Campus Connect - College Issues & Complaints System",
        layout,
        finalize=True,
        resizable=True,
        size=(960, 680)
    )

    # State variables
    current_complaints = []
    selected_complaint_id = None

    def refresh_table():
        nonlocal current_complaints
        st_filter = window["-FILTER-STATUS-"].get()
        cat_filter = window["-FILTER-CAT-"].get()
        pri_filter = window["-FILTER-PRIORITY-"].get()
        search_kw = window["-SEARCH-KEY-"].get()

        data, source = api_get_complaints(status=st_filter, category=cat_filter, priority=pri_filter, search=search_kw)
        current_complaints = data

        table_rows = []
        for c in data:
            created_short = c.get("created_at", "").split(" ")[0]
            table_rows.append([
                c.get("id"),
                c.get("ticket_id"),
                created_short,
                c.get("student_name"),
                c.get("roll_no"),
                c.get("department"),
                c.get("category"),
                c.get("priority"),
                c.get("status"),
                c.get("location"),
                c.get("title")
            ])
        window["-TABLE-"].update(values=table_rows)
        window["-STATUSBAR-"].update(f"Loaded {len(data)} complaints via [{source}] layer at {datetime.now().strftime('%H:%M:%S')}")
        update_analytics()

    def update_analytics():
        stats, source = api_get_stats()
        window["-STAT-TOTAL-"].update(str(stats.get("total", 0)))
        window["-STAT-OPEN-"].update(str(stats.get("open", 0)))
        window["-STAT-INPROG-"].update(str(stats.get("in_progress", 0)))
        window["-STAT-RESOLVED-"].update(str(stats.get("resolved", 0)))

        # Categories
        cat_lines = ["CATEGORY             COUNT", "--------------------------"]
        for cat, cnt in stats.get("by_category", {}).items():
            cat_lines.append(f"{cat[:18]:<20} {cnt}")
        window["-CAT-BREAKDOWN-"].update("\n".join(cat_lines))

        # Priorities
        pri_lines = ["PRIORITY             COUNT", "--------------------------"]
        for pri, cnt in stats.get("by_priority", {}).items():
            pri_lines.append(f"{pri:<20} {cnt}")
        window["-PRIORITY-BREAKDOWN-"].update("\n".join(pri_lines))

    def test_api():
        alive = check_api_status()
        if alive:
            window["-API-STATUS-LABEL-"].update("🟢 API Online (FastAPI connected)", text_color="#2ECC71")
            window["-MODE-BADGE-"].update("Mode: REST API Active", text_color="#2ECC71")
        else:
            window["-API-STATUS-LABEL-"].update("🟡 API Offline (Using SQLite fallback)", text_color="#F39C12")
            window["-MODE-BADGE-"].update("Mode: Local SQLite Active", text_color="#F39C12")

    # Initial load
    test_api()
    refresh_table()

    # Event Loop
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        # LODGE COMPLAINT SUBMIT
        if event == "-SUBMIT-":
            name = values["-NAME-"].strip()
            roll = values["-ROLL-"].strip()
            dept = values["-DEPT-"]
            location = values["-LOCATION-"].strip()
            email = values["-EMAIL-"].strip()
            phone = values["-PHONE-"].strip()
            category = values["-CAT-"]
            priority = values["-PRIORITY-"]
            title = values["-TITLE-"].strip()
            desc = values["-DESC-"].strip()

            if not name or not roll or not location or not email or not title or not desc:
                sg.popup_quick_message("⚠️ Please fill in all required fields marked with *", text_color="#E74C3C", auto_close_duration=3)
                continue

            payload = {
                "student_name": name,
                "roll_no": roll,
                "department": dept,
                "location": location,
                "email": email,
                "phone": phone,
                "category": category,
                "priority": priority,
                "title": title,
                "description": desc
            }

            created, source = api_create_complaint(payload)
            if created:
                ticket_code = created.get("ticket_id", "New Ticket")
                window["-SUBMIT-STATUS-"].update(f"✅ Success! Complaint Registered: {ticket_code} (via {source})")
                sg.popup(f"Complaint Registered Successfully!\n\nYour Ticket ID is: {ticket_code}\nPlease note this ticket ID for tracking.", title="Complaint Registered")
                # Reset inputs
                window["-TITLE-"].update("")
                window["-DESC-"].update("")
                window["-LOCATION-"].update("")
                refresh_table()
            else:
                sg.popup_error("Failed to register complaint. Please check your data and retry.")

        # CLEAR FORM
        if event == "-CLEAR-":
            for k in ["-NAME-", "-ROLL-", "-LOCATION-", "-EMAIL-", "-PHONE-", "-TITLE-", "-DESC-"]:
                window[k].update("")
            window["-SUBMIT-STATUS-"].update("")

        # FILTER & REFRESH
        if event in ("-APPLY-FILTER-", "-REFRESH-TABLE-"):
            refresh_table()

        # ROW SELECTION IN TABLE
        if event == "-TABLE-":
            selected_indices = values["-TABLE-"]
            if selected_indices:
                row_idx = selected_indices[0]
                if row_idx < len(current_complaints):
                    item = current_complaints[row_idx]
                    selected_complaint_id = item["id"]
                    window["-SEL-TICKET-"].update(item.get("ticket_id", ""))
                    window["-SEL-STUDENT-"].update(f"{item.get('student_name', '')} ({item.get('department', '')})")
                    window["-SEL-ROLL-"].update(item.get("roll_no", ""))
                    window["-SEL-LOC-"].update(item.get("location", ""))
                    window["-SEL-CONTACT-"].update(f"{item.get('email', '')} | {item.get('phone', '')}")
                    window["-SEL-DESC-"].update(item.get("description", ""))
                    window["-UPDATE-STATUS-"].update(item.get("status", "Open"))
                    window["-UPDATE-PRIORITY-"].update(item.get("priority", "Medium"))
                    window["-UPDATE-NOTES-"].update(item.get("admin_notes", ""))
                    window["-ACTION-MSG-"].update("")

        # UPDATE STATUS & NOTES
        if event == "-SAVE-UPDATE-":
            if not selected_complaint_id:
                sg.popup_quick_message("⚠️ Select a complaint from the table first.", text_color="#E67E22")
                continue

            new_status = values["-UPDATE-STATUS-"]
            new_priority = values["-UPDATE-PRIORITY-"]
            new_notes = values["-UPDATE-NOTES-"]

            updates = {
                "status": new_status,
                "priority": new_priority,
                "admin_notes": new_notes
            }

            updated, source = api_update_complaint(selected_complaint_id, updates)
            if updated:
                window["-ACTION-MSG-"].update("✅ Updated successfully!")
                refresh_table()
            else:
                sg.popup_error("Failed to update complaint.")

        # DELETE COMPLAINT
        if event == "-DELETE-TICKET-":
            if not selected_complaint_id:
                sg.popup_quick_message("⚠️ Select a complaint from the table first.", text_color="#E67E22")
                continue

            confirm = sg.popup_yes_no(f"Are you sure you want to permanently delete complaint ID {selected_complaint_id}?", title="Confirm Deletion")
            if confirm == "Yes":
                ok, source = api_delete_complaint(selected_complaint_id)
                if ok:
                    window["-ACTION-MSG-"].update("🗑️ Deleted successfully!")
                    selected_complaint_id = None
                    # Clear detail panel
                    window["-SEL-TICKET-"].update("None selected")
                    window["-SEL-STUDENT-"].update("-")
                    window["-SEL-ROLL-"].update("-")
                    window["-SEL-LOC-"].update("-")
                    window["-SEL-CONTACT-"].update("-")
                    window["-SEL-DESC-"].update("")
                    window["-UPDATE-NOTES-"].update("")
                    refresh_table()

        # EXPORT TO CSV
        if event == "-EXPORT-CSV-":
            if not current_complaints:
                sg.popup_quick_message("No complaints to export.", text_color="#E67E22")
                continue
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"campus_complaints_export_{timestamp}.csv")
            try:
                keys = current_complaints[0].keys()
                with open(export_path, "w", newline="", encoding="utf-8") as f:
                    dict_writer = csv.DictWriter(f, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(current_complaints)
                sg.popup(f"Successfully exported {len(current_complaints)} complaints to:\n{export_path}", title="Export Complete")
            except Exception as e:
                sg.popup_error(f"Error exporting CSV: {str(e)}")

        # TEST API CONNECTION
        if event == "-TEST-API-":
            test_api()

    window.close()

if __name__ == "__main__":
    create_gui_app()
