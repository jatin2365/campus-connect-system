"""
Campus Connect - FastAPI Backend REST API
Exposes RESTful endpoints for submitting, querying, updating, and analyzing
college campus issues and complaints.
"""

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import uvicorn
import database

# Initialize database
database.init_db()

app = FastAPI(
    title="Campus Connect - Issue & Complaint API",
    description="REST API for College Issues, Maintenance, Hostel, and Campus Complaints Management",
    version="1.0.0"
)

# Enable CORS for cross-platform and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class ComplaintCreateSchema(BaseModel):
    title: str = Field(..., example="Wi-Fi Not Working in CS Lab 3")
    category: str = Field(default="Infrastructure & IT", example="Infrastructure & IT")
    priority: str = Field(default="Medium", example="High")
    location: str = Field(..., example="CS Block, 2nd Floor, Lab 3")
    student_name: str = Field(..., example="John Doe")
    roll_no: str = Field(..., example="2023CS012")
    department: str = Field(default="Computer Science", example="Computer Science")
    email: str = Field(..., example="john.doe@college.edu")
    phone: str = Field(..., example="9876543210")
    description: str = Field(..., example="Ethernet cables are loose and Wi-Fi SSID is not broadcasting.")

class ComplaintUpdateSchema(BaseModel):
    status: Optional[str] = Field(None, example="In Progress")
    admin_notes: Optional[str] = Field(None, example="Assigned to network engineer. Replacement router requested.")
    priority: Optional[str] = Field(None, example="High")
    category: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

@app.get("/")
def root():
    return {
        "app": "Campus Connect API",
        "status": "Online",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "complaints": "/api/complaints",
            "statistics": "/api/stats"
        }
    }

@app.get("/api/health")
def health_check():
    stats = database.get_statistics()
    return {
        "status": "healthy",
        "service": "Campus Connect REST API",
        "total_records": stats["total"]
    }

@app.get("/api/complaints")
def list_complaints(
    status: Optional[str] = Query(None, description="Filter by status (Open, In Progress, Resolved)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search keyword in title, roll_no, ticket_id, or name")
):
    """List complaints with optional filtering and search."""
    return database.get_all_complaints(status=status, category=category, priority=priority, search=search)

@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: int):
    """Retrieve complaint details by numerical ID."""
    complaint = database.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint with ID {complaint_id} not found")
    return complaint

@app.get("/api/complaints/ticket/{ticket_id}")
def get_complaint_by_ticket(ticket_id: str):
    """Retrieve complaint details by Ticket ID (e.g. CC-1001)."""
    complaint = database.get_complaint_by_ticket(ticket_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return complaint

@app.post("/api/complaints", status_code=status.HTTP_201_CREATED)
def submit_complaint(payload: ComplaintCreateSchema):
    """Submit a new complaint."""
    try:
        created = database.create_complaint(payload.model_dump())
        return {
            "message": "Complaint successfully registered",
            "complaint": created
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lodge complaint: {str(e)}")

@app.put("/api/complaints/{complaint_id}")
def update_complaint_endpoint(complaint_id: int, payload: ComplaintUpdateSchema):
    """Update status, admin notes, or details of a complaint."""
    existing = database.get_complaint_by_id(complaint_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Complaint with ID {complaint_id} not found")
    
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = database.update_complaint(complaint_id, update_data)
    return {
        "message": "Complaint updated successfully",
        "complaint": updated
    }

@app.delete("/api/complaints/{complaint_id}")
def delete_complaint_endpoint(complaint_id: int):
    """Delete a complaint record."""
    success = database.delete_complaint(complaint_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Complaint with ID {complaint_id} not found")
    return {"message": f"Complaint {complaint_id} deleted successfully"}

@app.get("/api/stats")
def get_stats():
    """Retrieve college campus complaint statistics."""
    return database.get_statistics()

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Utility to run the API server."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    print("Starting Campus Connect API Server at http://127.0.0.1:8000 ...")
    start_server()
