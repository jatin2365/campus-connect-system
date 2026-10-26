# 🏛️ Campus Connect — College Issue & Complaint Management System

A college issue and complaint tracking platform featuring an SQLite database, FastAPI RESTful backend, and a PySimpleGUI desktop UI application, complete with a Jupyter Notebook.

---

## 🌟 Key Features

1. **Issue & Complaint Registration (Student/Faculty Portal)**:
   - Lodging across categories: *Infrastructure & IT*, *Academic & Classroom*, *Hostel & Mess*, *Campus Facilities*, *Admin & Accounts*, *Security & Transport*.
   - Priority levels: *Low*, *Medium*, *High*, *Urgent*.
   - Automatic generation of unique Ticket IDs (e.g., `CC-1001`, `CC-1002`).

2. **Resolution & Admin Tracking**:
   - Filterable table by status (*Open*, *In Progress*, *Resolved*), category, and priority.
   - Real-time search by Ticket ID, Student Name, Roll No, or keyword.
   - Status transitions, priority modification, and admin resolution remarks.
   - One-click export to CSV reports.

3. **Modern PySimpleGUI Desktop Client**:
   - Clean dark-teal theme (`DarkTeal9`).
   - 3-tab layout:
     - 📝 **Lodge Complaint**
     - 📋 **Manage & Track Complaints**
     - 📊 **Analytics & System Status**
   - Seamless fallback: Automatically connects to the FastAPI REST API or local SQLite database if the API is offline.

4. **FastAPI REST Backend**:
   - Fully asynchronous with Pydantic schema validation.
   - Interactive Swagger API docs (`/docs`) and OpenAPI spec (`/openapi.json`).
   - CRUD endpoints + real-time statistical aggregation.

5. **Self-Contained Jupyter Notebook (`campus_connect_system.ipynb`)**:
   - Step-by-step cells demonstrating database setup, API server in background thread, REST requests, GUI launcher, and Pandas analytics.

---

## 📁 Project Structure

```
pysimplegui/
├── campus_connect_system.ipynb   # 📓 Full Jupyter Notebook requested by user
├── run_all.py                   # 🚀 Master runner (Starts FastAPI + PySimpleGUI GUI)
├── gui_app.py                   # 🖥️ PySimpleGUI Desktop GUI application
├── api.py                       # ⚡ FastAPI REST API backend
├── database.py                  # 🗄️ SQLite database layer & seed data
├── campus_connect.db            # 💾 Local SQLite database file
└── README.md                    # 📖 Documentation & execution guide
```

---

## 🚀 How to Run

### Method 1: Run the Jupyter Notebook (Recommended)
Open and run the notebook in VS Code, JupyterLab, or Jupyter Notebook:
```bash
jupyter notebook campus_connect_system.ipynb
```
Follow the sequential cells to see the database initialization, FastAPI server launch in background thread, REST API queries, and the PySimpleGUI client.

---

### Method 2: One-Click Master Launcher (API + Desktop GUI)
Run both the FastAPI backend server and the PySimpleGUI desktop application together:
```bash
python run_all.py
```
This automatically:
1. Boots the FastAPI backend at `http://127.0.0.1:8000`.
2. Verifies API health.
3. Launches the PySimpleGUI window.

---

### Method 3: Run Components Individually

#### 1. Start the FastAPI Server:
```bash
python api.py
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`

#### 2. Start the PySimpleGUI Application:
```bash
python gui_app.py
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & system status |
| `GET` | `/api/complaints` | Query complaints (supports `status`, `category`, `priority`, `search`) |
| `GET` | `/api/complaints/{id}` | Get complaint details by numeric ID |
| `GET` | `/api/complaints/ticket/{ticket_id}` | Get complaint by ticket code (e.g. `CC-1001`) |
| `POST` | `/api/complaints` | Submit a new complaint |
| `PUT` | `/api/complaints/{id}` | Update status, admin notes, priority |
| `DELETE` | `/api/complaints/{id}` | Delete a complaint ticket |
| `GET` | `/api/stats` | Summary statistics (counts by status, category, priority) |

---

## 🗃️ Database Schema (`complaints`)

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-increment Primary Key |
| `ticket_id` | TEXT | Unique Ticket ID (`CC-1001`) |
| `title` | TEXT | Brief summary of the complaint |
| `category` | TEXT | Category (IT, Hostel, Academic, etc.) |
| `priority` | TEXT | `Low`, `Medium`, `High`, `Urgent` |
| `location` | TEXT | Campus block, floor, or room number |
| `student_name` | TEXT | Complainant name |
| `roll_no` | TEXT | College Roll / Registration number |
| `department` | TEXT | Department (e.g. Computer Science) |
| `email` | TEXT | Official contact email |
| `phone` | TEXT | Contact phone number |
| `description` | TEXT | Detailed explanation of the issue |
| `status` | TEXT | `Open`, `In Progress`, `Resolved` |
| `admin_notes` | TEXT | Remarks or action taken by college authority |
| `created_at` | TEXT | Timestamp of submission |
| `updated_at` | TEXT | Timestamp of last modification |
