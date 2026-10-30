
import shutil
import sqlite3
from pathlib import Path

from . import escalation

BASE_DIR = Path(__file__).parent.parent
TEST_DB = BASE_DIR / "data" / "escalation_test.db"


def main():
    shutil.copy2(BASE_DIR / "data" / "hr_policy.db", TEST_DB)
    escalation.DB_PATH = TEST_DB

    try:
        result = escalation.create_escalation(
            ticket_id="TKT00002",
            category="harassment",
            reason="Testing HR escalation workflow"
        )

        print("\nEscalation result:")
        print(result)

        connection = sqlite3.connect(TEST_DB)

        ticket = connection.execute(
            "SELECT status FROM Ticket WHERE ticket_id = ?",
            ("TKT00002",)
        ).fetchone()

        assignments = connection.execute(
            """
            SELECT assigned_queue, assignment_status
            FROM Assignment
            WHERE ticket_id = ?
            ORDER BY assigned_at
            """,
            ("TKT00002",)
        ).fetchall()

        events = connection.execute(
            """
            SELECT event_type, actor_type
            FROM TicketEvent
            WHERE ticket_id = ?
              AND event_type = 'escalated'
            """,
            ("TKT00002",)
        ).fetchall()

        connection.close()

        print("\nTicket status:", ticket)
        print("Assignment history:", assignments)
        print("Escalation events:", events)

        assert ticket[0] == "escalated"
        assert assignments[-1] == (
            "HR_EMPLOYEE_RELATIONS", "active"
        )
        assert assignments[0][1] == "reassigned"
        assert len(events) == 1

        print("\nAll escalation tests passed.")

    finally:
        if TEST_DB.exists():
            TEST_DB.unlink()


if __name__ == "__main__":
    main()
