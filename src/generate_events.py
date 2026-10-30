
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

try:
    events = []

    tickets = connection.execute("""
        SELECT
            ticket_id,
            requester_employee_id,
            status,
            created_at,
            resolved_at,
            closed_at
        FROM Ticket
        ORDER BY ticket_id
    """).fetchall()

    for ticket in tickets:
        (
            ticket_id,
            requester_id,
            status,
            created_at,
            resolved_at,
            closed_at
        ) = ticket

        events.append((
            f"EVT-{ticket_id}-CREATED",
            ticket_id,
            "ticket_created",
            "employee",
            requester_id,
            json.dumps({"status": "new"}),
            created_at
        ))

        assignment = connection.execute("""
            SELECT assigned_queue, assigned_employee_id, assigned_at
            FROM Assignment
            WHERE ticket_id = ?
        """, (ticket_id,)).fetchone()

        if assignment:
            queue, assigned_employee, assigned_at = assignment

            events.append((
                f"EVT-{ticket_id}-ASSIGNED",
                ticket_id,
                "assignment_changed",
                "system",
                None,
                json.dumps({
                    "queue": queue,
                    "assigned_employee": assigned_employee
                }),
                assigned_at
            ))

            events.append((
                f"EVT-{ticket_id}-QUEUE",
                ticket_id,
                "queue_changed",
                "system",
                None,
                json.dumps({"new_queue": queue}),
                assigned_at
            ))

        events.append((
            f"EVT-{ticket_id}-STATUS",
            ticket_id,
            "status_changed",
            "system",
            None,
            json.dumps({"current_status": status}),
            created_at
        ))

        if status == "escalated":
            events.append((
                f"EVT-{ticket_id}-ESCALATED",
                ticket_id,
                "escalated",
                "system",
                None,
                json.dumps({"reason": "Ticket requires further review"}),
                created_at
            ))

        if resolved_at:
            resolution = connection.execute("""
                SELECT resolution_type, resolved_by_type,
                       resolved_by_employee_id,
                       policy_version_id,
                       knowledge_article_id
                FROM Resolution
                WHERE ticket_id = ?
            """, (ticket_id,)).fetchone()

            if resolution:
                (
                    resolution_type,
                    actor_type,
                    actor_employee_id,
                    policy_version_id,
                    article_id
                ) = resolution

                events.append((
                    f"EVT-{ticket_id}-RESOLVED",
                    ticket_id,
                    "ticket_resolved",
                    actor_type,
                    actor_employee_id,
                    json.dumps({
                        "resolution_type": resolution_type
                    }),
                    resolved_at
                ))

                if policy_version_id:
                    events.append((
                        f"EVT-{ticket_id}-POLICY",
                        ticket_id,
                        "policy_cited",
                        "assistant",
                        None,
                        json.dumps({
                            "policy_version_id": policy_version_id,
                            "knowledge_article_id": article_id
                        }),
                        resolved_at
                    ))

        if closed_at:
            events.append((
                f"EVT-{ticket_id}-CLOSED",
                ticket_id,
                "ticket_closed",
                "system",
                None,
                json.dumps({"status": "closed"}),
                closed_at
            ))

    messages = connection.execute("""
        SELECT
            message_id,
            ticket_id,
            sender_type,
            sender_employee_id,
            created_at
        FROM Message
        ORDER BY ticket_id, sequence_number
    """).fetchall()

    for message in messages:
        (
            message_id,
            ticket_id,
            sender_type,
            sender_employee_id,
            created_at
        ) = message

        events.append((
            f"EVT-{message_id}",
            ticket_id,
            "message_added",
            sender_type,
            sender_employee_id,
            json.dumps({"message_id": message_id}),
            created_at
        ))

    connection.executemany("""
        INSERT OR IGNORE INTO TicketEvent (
            event_id,
            ticket_id,
            event_type,
            actor_type,
            actor_employee_id,
            event_details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, events)

    connection.commit()

    total = connection.execute(
        "SELECT COUNT(*) FROM TicketEvent"
    ).fetchone()[0]

    print("Audit event generation completed!")
    print("Total events:", total)

    print("\nEvents by type:")

    results = connection.execute("""
        SELECT event_type, COUNT(*)
        FROM TicketEvent
        GROUP BY event_type
        ORDER BY event_type
    """).fetchall()

    for result in results:
        print(result)

except sqlite3.Error as error:
    connection.rollback()
    print("Database error:", error)

finally:
    connection.close()
