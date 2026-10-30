
import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "hr_policy.db"


def create_escalation(ticket_id, category, reason):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    now = datetime.now(timezone.utc).isoformat()
    hr_queue = "HR_EMPLOYEE_RELATIONS"

    try:
        ticket = connection.execute(
            """
            SELECT ticket_id, status
            FROM Ticket
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found.")

        connection.execute(
            """
            UPDATE Assignment
            SET assignment_status = 'reassigned',
                ended_at = ?
            WHERE ticket_id = ?
              AND assignment_status = 'active'
            """,
            (now, ticket_id)
        )

        assignment_id = f"ASG-{uuid.uuid4().hex[:12]}"

        connection.execute(
            """
            INSERT INTO Assignment (
                assignment_id,
                ticket_id,
                assigned_queue,
                assignment_status,
                assignment_reason,
                assigned_at
            )
            VALUES (?, ?, ?, 'active', ?, ?)
            """,
            (
                assignment_id,
                ticket_id,
                hr_queue,
                reason,
                now
            )
        )

        connection.execute(
            """
            UPDATE Ticket
            SET status = 'escalated',
                updated_at = ?
            WHERE ticket_id = ?
            """,
            (now, ticket_id)
        )

        event_id = f"EVT-{uuid.uuid4().hex[:12]}"

        event_details = {
            "category": category,
            "assigned_queue": hr_queue,
            "reason": reason,
            "assignment_id": assignment_id
        }

        connection.execute(
            """
            INSERT INTO TicketEvent (
                event_id,
                ticket_id,
                event_type,
                actor_type,
                event_details,
                created_at
            )
            VALUES (?, ?, 'escalated', 'system', ?, ?)
            """,
            (
                event_id,
                ticket_id,
                json.dumps(event_details),
                now
            )
        )

        connection.commit()

        return {
            "ticket_id": ticket_id,
            "status": "escalated",
            "assigned_queue": hr_queue,
            "assignment_id": assignment_id,
            "category": category,
            "reason": reason
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
