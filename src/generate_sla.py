
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

now = "2026-01-01T10:00:00"

categories = [
    ("CAT001", "benefits", "Benefits", "HR_BENEFITS", "normal", 60, 1440, 0),
    ("CAT002", "leave", "Leave", "HR_OPERATIONS", "normal", 60, 1440, 0),
    ("CAT003", "payroll", "Payroll", "PAYROLL_HR", "high", 30, 720, 0),
    ("CAT004", "onboarding", "Onboarding", "HR_ONBOARDING", "normal", 120, 2880, 0),
    ("CAT005", "employee_relations", "Employee Relations", "HR_RESTRICTED", "high", 30, 720, 1),
    ("CAT006", "general", "General Queries", "HR_GENERAL", "low", 240, 4320, 0),
]

priorities = {
    "urgent": (15, 240),
    "high": (30, 480),
    "normal": (60, 1440),
    "low": (240, 4320),
}

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

try:
    for category in categories:
        connection.execute("""
            INSERT OR IGNORE INTO Category (
                category_id,
                category_code,
                category_name,
                default_queue,
                default_priority,
                default_response_minutes,
                default_resolution_minutes,
                requires_restricted_handling,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, category)

    for category in categories:
        category_id = category[0]
        category_code = category[1]

        for priority, targets in priorities.items():
            response_minutes, resolution_minutes = targets

            if priority == "urgent":
                calendar_type = "24x7"
                business_start = None
                business_end = None
            else:
                calendar_type = "business_hours"
                business_start = "09:00"
                business_end = "18:00"

            sla_id = f"SLA-{category_code.upper()}-{priority.upper()}"

            connection.execute("""
                INSERT OR IGNORE INTO SLA (
                    sla_id,
                    sla_name,
                    category_id,
                    priority,
                    calendar_type,
                    response_target_minutes,
                    resolution_target_minutes,
                    business_start_local,
                    business_end_local,
                    business_days,
                    timezone,
                    effective_start,
                    effective_end,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 1)
            """, (
                sla_id,
                f"{category_code.title()} - {priority.title()} SLA",
                category_id,
                priority,
                calendar_type,
                response_minutes,
                resolution_minutes,
                business_start,
                business_end,
                "[1,2,3,4,5]",
                "Asia/Kolkata",
                "2026-01-01"
            ))

    connection.commit()

    print("Category and SLA data generated successfully!")

    for table in ["Category", "SLA"]:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table}: {count}")

    print("\nSLA calendar distribution:")
    results = connection.execute("""
        SELECT calendar_type, COUNT(*)
        FROM SLA
        GROUP BY calendar_type
    """).fetchall()

    for result in results:
        print(result)

except sqlite3.Error as error:
    connection.rollback()
    print("Database error:", error)

finally:
    connection.close()
