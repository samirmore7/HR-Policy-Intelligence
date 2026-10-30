
import sqlite3
import random
from pathlib import Path

random.seed(20261022)

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

try:
    tickets = connection.execute("""
        SELECT
            t.ticket_id,
            t.category_id,
            t.priority,
            t.sensitivity,
            t.status,
            t.created_at,
            t.resolved_at,
            c.category_code,
            c.default_queue
        FROM Ticket t
        JOIN Category c ON t.category_id = c.category_id
        ORDER BY t.ticket_id
    """).fetchall()

    hr_employees = [
        row[0] for row in connection.execute("""
            SELECT employee_id
            FROM Employee
            WHERE employee_type = 'hr_partner'
        """).fetchall()
    ]

    articles = {}

    article_records = connection.execute("""
        SELECT
            d.category_code,
            a.knowledge_article_id,
            a.policy_version_id
        FROM KnowledgeArticle a
        JOIN PolicyVersion v
            ON a.policy_version_id = v.policy_version_id
        JOIN PolicyDocument d
            ON v.policy_id = d.policy_id
        WHERE a.is_active = 1
          AND v.status = 'effective'
    """).fetchall()

    for category_code, article_id, version_id in article_records:
        articles.setdefault(category_code, []).append(
            (article_id, version_id)
        )

    assignments = []
    resolutions = []

    for ticket in tickets:
        (
            ticket_id,
            category_id,
            priority,
            sensitivity,
            status,
            created_at,
            resolved_at,
            category_code,
            default_queue
        ) = ticket

        restricted = sensitivity == "restricted"

        assigned_queue = (
            "HR_RESTRICTED" if restricted else default_queue
        )

        needs_hr = (
            restricted
            or status in (
                "assigned",
                "in_progress",
                "escalated",
                "reopened"
            )
        )

        assigned_employee_id = (
            random.choice(hr_employees) if needs_hr else None
        )

        assignment_status = (
            "completed"
            if status in ("resolved", "closed")
            else "active"
        )

        ended_at = (
            resolved_at
            if assignment_status == "completed"
            else None
        )

        assignment_id = f"ASN-{ticket_id}"

        assignments.append((
            assignment_id,
            ticket_id,
            assigned_queue,
            assigned_employee_id,
            assignment_status,
            "Initial ticket routing",
            created_at,
            ended_at
        ))

        if status not in ("resolved", "closed"):
            continue

        resolution_id = f"RES-{ticket_id}"

        if restricted:
            resolution_type = "hr_handoff"
            summary = (
                "Sensitive request handled through restricted HR review."
            )
            policy_version_id = None
            knowledge_article_id = None
            resolved_by_type = "hr_agent"
            resolved_by_employee_id = assigned_employee_id

        else:
            available_articles = articles.get(category_code, [])

            if not available_articles:
                raise ValueError(
                    f"No effective article found for {category_code}"
                )

            knowledge_article_id, policy_version_id = random.choice(
                available_articles
            )

            resolution_type = "policy_answer"
            summary = (
                "Ticket resolved using the applicable published HR policy."
            )
            resolved_by_type = "assistant"
            resolved_by_employee_id = None

        resolutions.append((
            resolution_id,
            ticket_id,
            resolution_type,
            summary,
            round(random.uniform(0.75, 0.99), 2),
            policy_version_id,
            knowledge_article_id,
            resolved_by_type,
            resolved_by_employee_id,
            resolved_at
        ))

    connection.executemany("""
        INSERT OR IGNORE INTO Assignment (
            assignment_id,
            ticket_id,
            assigned_queue,
            assigned_employee_id,
            assignment_status,
            assignment_reason,
            assigned_at,
            ended_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, assignments)

    connection.executemany("""
        INSERT OR IGNORE INTO Resolution (
            resolution_id,
            ticket_id,
            resolution_type,
            resolution_summary,
            confidence_score,
            policy_version_id,
            knowledge_article_id,
            resolved_by_type,
            resolved_by_employee_id,
            resolved_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, resolutions)

    connection.commit()

    print("Workflow data generated successfully!")

    for table in ("Assignment", "Resolution"):
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table}: {count}")

    print("\nAssignments by queue:")
    for row in connection.execute("""
        SELECT assigned_queue, COUNT(*)
        FROM Assignment
        GROUP BY assigned_queue
        ORDER BY assigned_queue
    """):
        print(row)

    print("\nResolutions by type:")
    for row in connection.execute("""
        SELECT resolution_type, COUNT(*)
        FROM Resolution
        GROUP BY resolution_type
    """):
        print(row)

except (sqlite3.Error, ValueError) as error:
    connection.rollback()
    print("Error:", error)

finally:
    connection.close()
