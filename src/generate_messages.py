
import sqlite3
import random
from pathlib import Path

random.seed(20261022)

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

assistant_replies = [
    "I have received your request. Let me check the applicable HR policy.",
    "I found relevant information in the HR policy knowledge base.",
    "Your request is being reviewed. I will share the next steps shortly.",
    "I may need additional information to provide an accurate answer.",
]

hr_replies = [
    "Our HR team has reviewed your request. Please contact us if you need further assistance.",
    "We have checked the relevant details and will guide you through the next steps.",
    "Your concern has been forwarded to the appropriate HR representative.",
    "Thank you for reaching out. Our team is available to assist you.",
]

final_replies = [
    "Thank you for contacting the HR service desk.",
    "Please refer to the applicable policy for complete details.",
    "Your request has been updated. Let us know if you need further help.",
    "We appreciate your patience while we review your request.",
]

try:
    tickets = connection.execute("""
        SELECT
            ticket_id,
            requester_employee_id,
            category_id,
            sensitivity,
            status,
            initial_question
        FROM Ticket
        ORDER BY ticket_id
    """).fetchall()

    hr_employees = connection.execute("""
        SELECT employee_id
        FROM Employee
        WHERE employee_type = 'hr_partner'
    """).fetchall()

    if not tickets:
        raise ValueError("No tickets found. Generate tickets first.")

    if not hr_employees:
        raise ValueError("No HR partners found.")

    messages = []

    for ticket in tickets:
        (
            ticket_id,
            requester_id,
            category_id,
            sensitivity,
            status,
            question
        ) = ticket

        hr_employee_id = random.choice(hr_employees)[0]

        conversation = [
            (
                "employee",
                requester_id,
                question,
                0
            ),
            (
                "assistant",
                None,
                random.choice(assistant_replies),
                0
            ),
        ]

        if sensitivity == "restricted":
            conversation.append((
                "hr_agent",
                hr_employee_id,
                "Internal note: This sensitive request requires restricted HR handling.",
                1
            ))

            conversation.append((
                "hr_agent",
                hr_employee_id,
                random.choice(hr_replies),
                0
            ))

        elif status in ("escalated", "in_progress", "assigned", "reopened"):
            conversation.append((
                "hr_agent",
                hr_employee_id,
                random.choice(hr_replies),
                0
            ))

            conversation.append((
                "assistant",
                None,
                random.choice(final_replies),
                0
            ))

        else:
            conversation.append((
                "assistant",
                None,
                "I have checked the available HR policy information and prepared an update for your request.",
                0
            ))

            conversation.append((
                "assistant",
                None,
                random.choice(final_replies),
                0
            ))

        created_at = connection.execute(
            "SELECT created_at FROM Ticket WHERE ticket_id = ?",
            (ticket_id,)
        ).fetchone()[0]

        for sequence, message in enumerate(conversation, start=1):
            sender_type, sender_id, message_text, is_internal = message

            message_id = f"MSG-{ticket_id}-{sequence:03d}"

            messages.append((
                message_id,
                ticket_id,
                sequence,
                sender_type,
                sender_id,
                message_text,
                created_at,
                is_internal
            ))

    connection.executemany("""
        INSERT OR IGNORE INTO Message (
            message_id,
            ticket_id,
            sequence_number,
            sender_type,
            sender_employee_id,
            message_text,
            created_at,
            is_internal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, messages)

    connection.commit()

    total = connection.execute(
        "SELECT COUNT(*) FROM Message"
    ).fetchone()[0]

    print("Message generation completed!")
    print("Total messages:", total)

    print("\nMessages by sender:")
    results = connection.execute("""
        SELECT sender_type, COUNT(*)
        FROM Message
        GROUP BY sender_type
        ORDER BY sender_type
    """).fetchall()

    for result in results:
        print(result)

    print("\nInternal messages:",
          connection.execute("""
              SELECT COUNT(*)
              FROM Message
              WHERE is_internal = 1
          """).fetchone()[0])

except (sqlite3.Error, ValueError) as error:
    connection.rollback()
    print("Error:", error)

finally:
    connection.close()
