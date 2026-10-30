
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

app = FastAPI(
    title="HR Policy Intelligence API",
    description="API for HR tickets, conversations and workflows.",
    version="1.0.0"
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "HR Policy Intelligence"
    }


@app.get("/tickets")
def get_tickets(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    connection = get_connection()

    try:
        tickets = connection.execute("""
            SELECT
                t.ticket_id,
                t.subject,
                t.priority,
                t.sensitivity,
                t.status,
                t.channel,
                t.created_at,
                c.category_name,
                e.display_name AS requester
            FROM Ticket t
            JOIN Category c
                ON t.category_id = c.category_id
            JOIN Employee e
                ON t.requester_employee_id = e.employee_id
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        total = connection.execute(
            "SELECT COUNT(*) FROM Ticket"
        ).fetchone()[0]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "tickets": [dict(ticket) for ticket in tickets]
        }

    finally:
        connection.close()


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    connection = get_connection()

    try:
        ticket = connection.execute("""
            SELECT
                t.*,
                c.category_name,
                e.display_name AS requester,
                s.sla_name,
                s.calendar_type,
                s.response_target_minutes,
                s.resolution_target_minutes
            FROM Ticket t
            JOIN Category c
                ON t.category_id = c.category_id
            JOIN Employee e
                ON t.requester_employee_id = e.employee_id
            JOIN SLA s
                ON t.sla_id = s.sla_id
            WHERE t.ticket_id = ?
        """, (ticket_id,)).fetchone()

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        assignment = connection.execute("""
            SELECT
                assigned_queue,
                assigned_employee_id,
                assignment_status,
                assigned_at
            FROM Assignment
            WHERE ticket_id = ?
            ORDER BY assigned_at DESC
            LIMIT 1
        """, (ticket_id,)).fetchone()

        resolution = connection.execute("""
            SELECT *
            FROM Resolution
            WHERE ticket_id = ?
        """, (ticket_id,)).fetchone()

        return {
            "ticket": dict(ticket),
            "assignment": dict(assignment) if assignment else None,
            "resolution": dict(resolution) if resolution else None
        }

    finally:
        connection.close()


@app.get("/tickets/{ticket_id}/messages")
def get_ticket_messages(ticket_id: str):
    connection = get_connection()

    try:
        exists = connection.execute("""
            SELECT ticket_id
            FROM Ticket
            WHERE ticket_id = ?
        """, (ticket_id,)).fetchone()

        if not exists:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        messages = connection.execute("""
            SELECT
                message_id,
                sequence_number,
                sender_type,
                message_text,
                created_at
            FROM Message
            WHERE ticket_id = ?
              AND is_internal = 0
            ORDER BY sequence_number
        """, (ticket_id,)).fetchall()

        return {
            "ticket_id": ticket_id,
            "messages": [dict(message) for message in messages]
        }

    finally:
        connection.close()
