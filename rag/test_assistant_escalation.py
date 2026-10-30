
import shutil
import sqlite3
from pathlib import Path

from .assistant import HRPolicyAssistant
from . import escalation

BASE_DIR = Path(__file__).parent.parent
TEST_DB = BASE_DIR / "data" / "assistant_test.db"


def main():
    shutil.copy2(BASE_DIR / "data" / "hr_policy.db", TEST_DB)
    escalation.DB_PATH = TEST_DB

    try:
        assistant = HRPolicyAssistant()

        question = "I want to report sexual harassment at work."

        result = assistant.ask(
            question,
            ticket_id="TKT00002"
        )

        print("\nEmployee question:")
        print(question)

        print("\nAssistant response:")
        print(result)

        connection = sqlite3.connect(TEST_DB)

        ticket = connection.execute(
            "SELECT status FROM Ticket WHERE ticket_id = ?",
            ("TKT00002",)
        ).fetchone()

        assignment = connection.execute(
            """
            SELECT assigned_queue, assignment_status
            FROM Assignment
            WHERE ticket_id = ?
              AND assignment_status = 'active'
            """,
            ("TKT00002",)
        ).fetchone()

        event = connection.execute(
            """
            SELECT event_type
            FROM TicketEvent
            WHERE ticket_id = ?
              AND event_type = 'escalated'
            """,
            ("TKT00002",)
        ).fetchall()

        connection.close()

        print("\nDatabase verification:")
        print("Ticket status:", ticket)
        print("Active assignment:", assignment)
        print("Escalation events:", event)

        assert result["requires_human"] is True
        assert result["escalation"] is not None
        assert ticket[0] == "escalated"
        assert assignment[0] == "HR_EMPLOYEE_RELATIONS"
        assert len(event) == 1

        print("\nAll integration tests passed.")

    finally:
        if TEST_DB.exists():
            TEST_DB.unlink()


if __name__ == "__main__":
    main()
