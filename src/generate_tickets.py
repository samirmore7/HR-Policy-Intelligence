
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(20261022)

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

start_date = datetime(2026, 1, 1, 9, 0)
end_date = datetime(2026, 9, 30, 18, 0)

ticket_templates = {
    "benefits": [
        ("Health insurance coverage", "I need information about my health insurance coverage."),
        ("Dependent insurance", "How can I add a dependent to my insurance plan?"),
        ("Wellness benefits", "What wellness benefits are available to employees?"),
        ("Insurance claim process", "How do I submit an insurance claim?"),
    ],
    "leave": [
        ("Annual leave balance", "How can I check my remaining annual leave balance?"),
        ("Sick leave request", "I need help submitting a sick leave request."),
        ("Parental leave eligibility", "What is the eligibility process for parental leave?"),
        ("Leave approval status", "Can you help me check my leave approval status?"),
    ],
    "payroll": [
        ("Salary credit issue", "My salary has not been credited. Can you help?"),
        ("Payslip request", "Where can I download my monthly payslip?"),
        ("Tax documentation", "How can I obtain my tax documents?"),
        ("Overtime payment", "I have a question about my overtime payment."),
    ],
    "onboarding": [
        ("Joining documentation", "Which documents are required during onboarding?"),
        ("Background verification", "What is the status of my background verification?"),
        ("Employee ID creation", "When will I receive my employee ID?"),
        ("Onboarding portal access", "I cannot access the onboarding portal."),
    ],
    "employee_relations": [
        ("Workplace grievance", "I want to report a workplace concern."),
        ("Workplace conduct", "I need guidance about a workplace conduct issue."),
        ("Harassment concern", "I need confidential assistance with a sensitive workplace matter."),
        ("Disciplinary process", "I have a question about a disciplinary process."),
    ],
    "general": [
        ("Remote work request", "What is the process for requesting remote work?"),
        ("Attendance correction", "I need help correcting my attendance record."),
        ("Travel reimbursement", "How can I submit a travel reimbursement claim?"),
        ("Employee referral", "How does the employee referral process work?"),
        ("Information security", "I need guidance about information security requirements."),
    ],
}

priorities = ["low", "normal", "high", "urgent"]
priority_weights = [15, 50, 25, 10]

statuses = [
    "new",
    "triaged",
    "awaiting_clarification",
    "assigned",
    "in_progress",
    "escalated",
    "resolved",
    "closed",
    "reopened",
]

status_weights = [5, 10, 8, 12, 15, 8, 22, 15, 5]

channels = ["portal", "email", "chat", "api"]
channel_weights = [55, 20, 20, 5]

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

try:
    categories = connection.execute("""
        SELECT category_id, category_code
        FROM Category
    """).fetchall()

    employees = connection.execute("""
        SELECT employee_id
        FROM Employee
        WHERE employee_type = 'employee'
    """).fetchall()

    sla_records = connection.execute("""
        SELECT sla_id, category_id, priority
        FROM SLA
    """).fetchall()

    sla_lookup = {
        (category_id, priority): sla_id
        for sla_id, category_id, priority in sla_records
    }

    category_lookup = {
        code: category_id
        for category_id, code in categories
    }

    if len(categories) != 6 or len(employees) == 0:
        raise ValueError("Category or employee data is missing.")

    tickets = []

    for i in range(1, 5001):
        category_code = random.choice(list(ticket_templates))
        category_id = category_lookup[category_code]

        subject, question = random.choice(
            ticket_templates[category_code]
        )

        priority = random.choices(
            priorities,
            weights=priority_weights
        )[0]

        status = random.choices(
            statuses,
            weights=status_weights
        )[0]

        requester_id = random.choice(employees)[0]
        channel = random.choices(
            channels,
            weights=channel_weights
        )[0]

        created_at = start_date + timedelta(
            seconds=random.randint(
                0,
                int((end_date - start_date).total_seconds())
            )
        )

        first_response_at = None
        resolved_at = None
        closed_at = None

        if status != "new":
            first_response_at = created_at + timedelta(
                minutes=random.randint(5, 240)
            )

        if status in ("resolved", "closed"):
            resolved_at = created_at + timedelta(
                hours=random.randint(2, 120)
            )

        if status == "closed":
            closed_at = resolved_at + timedelta(
                hours=random.randint(1, 48)
            )

        updated_at = max(
            filter(None, [
                created_at,
                first_response_at,
                resolved_at,
                closed_at
            ])
        )

        updated_at += timedelta(
            minutes=random.randint(1, 60)
        )

        sensitivity = (
            "restricted"
            if category_code == "employee_relations"
            else random.choices(
                ["normal", "confidential"],
                weights=[90, 10]
            )[0]
        )

        sla_id = sla_lookup.get((category_id, priority))

        if not sla_id:
            raise ValueError(
                f"Missing SLA for {category_code} / {priority}"
            )

        tickets.append((
            f"TKT{i:05d}",
            requester_id,
            category_id,
            subject,
            question,
            priority,
            sensitivity,
            status,
            channel,
            created_at.isoformat(),
            updated_at.isoformat(),
            first_response_at.isoformat() if first_response_at else None,
            resolved_at.isoformat() if resolved_at else None,
            closed_at.isoformat() if closed_at else None,
            sla_id
        ))

    connection.executemany("""
        INSERT OR IGNORE INTO Ticket (
            ticket_id,
            requester_employee_id,
            category_id,
            subject,
            initial_question,
            priority,
            sensitivity,
            status,
            channel,
            created_at,
            updated_at,
            first_response_at,
            resolved_at,
            closed_at,
            sla_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets)

    connection.commit()

    total = connection.execute(
        "SELECT COUNT(*) FROM Ticket"
    ).fetchone()[0]

    print("Ticket generation completed!")
    print("Total tickets:", total)

    print("\nTickets by category:")
    results = connection.execute("""
        SELECT c.category_code, COUNT(*)
        FROM Ticket t
        JOIN Category c ON t.category_id = c.category_id
        GROUP BY c.category_code
        ORDER BY c.category_code
    """).fetchall()

    for result in results:
        print(result)

    print("\nTickets by status:")
    results = connection.execute("""
        SELECT status, COUNT(*)
        FROM Ticket
        GROUP BY status
        ORDER BY status
    """).fetchall()

    for result in results:
        print(result)

except (sqlite3.Error, ValueError) as error:
    connection.rollback()
    print("Error:", error)

finally:
    connection.close()
