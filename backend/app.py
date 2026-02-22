from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from classifier import predict_category
from regex_extractor import extract_account_id, extract_amount
from database import init_db, get_connection

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Complaint(BaseModel):
    customer_id: str
    complaint: str


@app.post("/predict")
def analyze(data: Complaint):
    customer_id = data.customer_id.strip()
    text = data.complaint.strip()

    category = predict_category(text)
    account_id = extract_account_id(text)
    amount = extract_amount(text)

    team_map = {
        "network_issue": "Network Team",
        "billing_issue": "Billing Team",
        "sim_issue": "SIM Support",
        "recharge_issue": "Recharge Desk",
        "general_query": "Customer Care"
    }

    team = team_map.get(category, "Customer Care")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints (customer_id, text, category, account_id, amount, team, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, text, category, account_id, amount, team, "Open", created_at))

    conn.commit()

    # ✅ get inserted id for frontend usage
    new_id = cursor.lastrowid
    conn.close()

    return {
        "id": new_id,
        "customer_id": customer_id,
        "text": text,
        "category": category,
        "account_id": account_id,
        "amount": amount,
        "team": team,
        "status": "Open",
        "created_at": created_at
    }


# ✅ GET ALL complaints (JSON list)
@app.get("/complaints")
def get_complaints():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


# ✅ GET HISTORY by customer_id (JSON list)
@app.get("/history/{customer_id}")
def get_history(customer_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer_id, text, category, account_id, amount, team, status, created_at
        FROM complaints
        WHERE customer_id = ?
        ORDER BY id DESC
    """, (customer_id,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


# ✅ Toggle status (returns JSON)
@app.put("/complaints/{complaint_id}")
def update_status(complaint_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM complaints WHERE id = ?", (complaint_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {"error": "Complaint not found"}

    current_status = result["status"]
    new_status = "Closed" if current_status == "Open" else "Open"

    cursor.execute(
        "UPDATE complaints SET status = ? WHERE id = ?",
        (new_status, complaint_id)
    )

    conn.commit()
    conn.close()

    return {"message": "Status updated", "new_status": new_status}