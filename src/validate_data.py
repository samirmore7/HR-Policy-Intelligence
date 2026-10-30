
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

checks = []


def run_check(name, query, expected=0):
    result = connection.execute(query).fetchone()
    value = result[0] if result else 0

    passed = value == expected
    checks.append(passed)

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {value}")


try:
    print("\nDATABASE INTEGRITY CHECKS\n")

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    checks.append(len(foreign_keys) == 0)

    print(
        f"[{'PASS' if not foreign_keys else 'FAIL'}] "
        f"Foreign key violations: {len(foreign_keys)}"
    )

    print("\nRECORD COUNT CHECKS\n")

    run_check(
        "Departments",
        "SELECT COUNT(*) FROM Department",
        6
    )

    run_check(
        "Employees",
        "SELECT COUNT(*) FROM Employee",
        118
    )

    run_check(
        "Policy documents",
        "SELECT COUNT(*) FROM PolicyDocument",
        25
    )

    run_check(
        "Policy versions",
        "SELECT COUNT(*) FROM PolicyVersion",
        30
    )

    run_check(
        "Knowledge articles",
        "SELECT COUNT(*) FROM KnowledgeArticle",
        150
    )

    run_check(
        "Categories",
        "SELECT COUNT(*) FROM Category",
        6
    )

    run_check(
        "SLA rules",
        "SELECT COUNT(*) FROM SLA",
        24
    )

    run_check(
        "Tickets",
        "SELECT COUNT(*) FROM Ticket",
        5000
    )

    run_check(
        "Messages",
        "SELECT COUNT(*) FROM Message",
        20000
    )

    run_check(
        "Assignments",
        "SELECT COUNT(*) FROM Assignment",
        5000
    )

    print("\nRELATIONSHIP CHECKS\n")

    run_check(
        "Tickets without assignments",
        """
        SELECT COUNT(*)
        FROM Ticket t
        LEFT JOIN Assignment a
            ON t.ticket_id = a.ticket_id
        WHERE a.assignment_id IS NULL
        """
    )

    run_check(
        "Resolved tickets without resolutions",
        """
        SELECT COUNT(*)
        FROM Ticket t
        LEFT JOIN Resolution r
            ON t.ticket_id = r.ticket_id
        WHERE t.status IN ('resolved', 'closed')
          AND r.resolution_id IS NULL
        """
    )

    run_check(
        "Resolutions linked to non-resolved tickets",
        """
        SELECT COUNT(*)
        FROM Resolution r
        JOIN Ticket t ON r.ticket_id = t.ticket_id
        WHERE t.status NOT IN ('resolved', 'closed')
        """
    )

    run_check(
        "Tickets with incorrect message count",
        """
        SELECT COUNT(*)
        FROM (
            SELECT t.ticket_id
            FROM Ticket t
            LEFT JOIN Message m ON t.ticket_id = m.ticket_id
            GROUP BY t.ticket_id
            HAVING COUNT(m.message_id) != 4
        )
        """
    )

    print("\nSENSITIVE HANDLING CHECKS\n")

    run_check(
        "Restricted tickets in incorrect queues",
        """
        SELECT COUNT(*)
        FROM Ticket t
        JOIN Assignment a ON t.ticket_id = a.ticket_id
        WHERE t.sensitivity = 'restricted'
          AND a.assigned_queue != 'HR_RESTRICTED'
        """
    )

    run_check(
        "Internal messages on non-restricted tickets",
        """
        SELECT COUNT(*)
        FROM Message m
        JOIN Ticket t ON m.ticket_id = t.ticket_id
        WHERE m.is_internal = 1
          AND t.sensitivity != 'restricted'
        """
    )

    print("\nPOLICY GROUNDING CHECKS\n")

    run_check(
        "Policy answers without policy references",
        """
        SELECT COUNT(*)
        FROM Resolution
        WHERE resolution_type = 'policy_answer'
          AND (
              policy_version_id IS NULL
              OR knowledge_article_id IS NULL
          )
        """
    )

    run_check(
        "Policy answers citing non-effective versions",
        """
        SELECT COUNT(*)
        FROM Resolution r
        JOIN PolicyVersion v
            ON r.policy_version_id = v.policy_version_id
        WHERE r.resolution_type = 'policy_answer'
          AND v.status != 'effective'
        """
    )

    run_check(
        "Policy articles linked to incorrect versions",
        """
        SELECT COUNT(*)
        FROM Resolution r
        JOIN KnowledgeArticle a
            ON r.knowledge_article_id = a.knowledge_article_id
        WHERE r.resolution_type = 'policy_answer'
          AND r.policy_version_id != a.policy_version_id
        """
    )

    print("\nAUDIT CHECKS\n")

    run_check(
        "Tickets without creation events",
        """
        SELECT COUNT(*)
        FROM Ticket t
        WHERE NOT EXISTS (
            SELECT 1
            FROM TicketEvent e
            WHERE e.ticket_id = t.ticket_id
              AND e.event_type = 'ticket_created'
        )
        """
    )

    run_check(
        "Messages without audit events",
        """
        SELECT COUNT(*)
        FROM Message m
        WHERE NOT EXISTS (
            SELECT 1
            FROM TicketEvent e
            WHERE e.event_type = 'message_added'
              AND json_extract(
                  e.event_details, '$.message_id'
              ) = m.message_id
        )
        """
    )

    print("\nFINAL RESULT\n")

    passed = sum(checks)
    total = len(checks)

    print(f"Checks passed: {passed}/{total}")

    if passed == total:
        print("All validation checks passed!")
    else:
        print("Some validation checks failed. Review the results.")

except sqlite3.Error as error:
    print("Database error:", error)

finally:
    connection.close()
