
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(20261022)

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

now = datetime(2026, 10, 1, 10, 0, 0)

policies = [
    ("POL001", "LEAVE01", "Annual Leave Policy", "leave", "DEP001"),
    ("POL002", "LEAVE02", "Sick Leave Policy", "leave", "DEP001"),
    ("POL003", "LEAVE03", "Parental Leave Policy", "leave", "DEP001"),
    ("POL004", "LEAVE04", "Public Holiday Policy", "leave", "DEP001"),
    ("POL005", "LEAVE05", "Unpaid Leave Policy", "leave", "DEP001"),
    ("POL006", "PAY001", "Salary Administration Policy", "payroll", "DEP003"),
    ("POL007", "PAY002", "Payroll Processing Policy", "payroll", "DEP003"),
    ("POL008", "PAY003", "Overtime Payment Policy", "payroll", "DEP003"),
    ("POL009", "PAY004", "Tax Documentation Policy", "payroll", "DEP003"),
    ("POL010", "BEN001", "Health Insurance Policy", "benefits", "DEP001"),
    ("POL011", "BEN002", "Wellness Benefits Policy", "benefits", "DEP001"),
    ("POL012", "BEN003", "Retirement Benefits Policy", "benefits", "DEP003"),
    ("POL013", "BEN004", "Employee Assistance Policy", "benefits", "DEP001"),
    ("POL014", "ONB001", "New Employee Onboarding Policy", "onboarding", "DEP001"),
    ("POL015", "ONB002", "Background Verification Policy", "onboarding", "DEP001"),
    ("POL016", "ONB003", "Employee Documentation Policy", "onboarding", "DEP001"),
    ("POL017", "ER001", "Workplace Conduct Policy", "employee_relations", "DEP001"),
    ("POL018", "ER002", "Grievance Handling Policy", "employee_relations", "DEP001"),
    ("POL019", "ER003", "Anti Harassment Policy", "employee_relations", "DEP001"),
    ("POL020", "ER004", "Disciplinary Action Policy", "employee_relations", "DEP001"),
    ("POL021", "GEN001", "Remote Work Policy", "general", "DEP002"),
    ("POL022", "GEN002", "Attendance Policy", "general", "DEP001"),
    ("POL023", "GEN003", "Information Security Policy", "general", "DEP006"),
    ("POL024", "GEN004", "Travel and Expense Policy", "general", "DEP003"),
    ("POL025", "GEN005", "Employee Referral Policy", "general", "DEP001"),
]

topics = [
    "Overview and eligibility",
    "How to submit a request",
    "Approval process",
    "Required documents",
    "Important timelines",
    "Exceptions and support",
]

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

try:
    for policy_id, code, title, category, department_id in policies:
        created_at = "2024-01-01T10:00:00"

        connection.execute("""
            INSERT OR IGNORE INTO PolicyDocument (
                policy_id,
                policy_code,
                title,
                category_code,
                owner_department_id,
                description,
                lifecycle_state,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            policy_id,
            code,
            title,
            category,
            department_id,
            f"Sample company policy covering {title.lower()}.",
            "published",
            created_at,
            now.isoformat()
        ))

        version_count = 2 if int(policy_id[-3:]) <= 5 else 1

        for version_number in range(1, version_count + 1):
            version_id = f"{policy_id}-V{version_number}"

            if version_number == 1 and version_count == 2:
                effective_start = "2024-01-01"
                effective_end = "2025-12-31"
                status = "superseded"
            elif version_number == 2:
                effective_start = "2026-01-01"
                effective_end = None
                status = "effective"
            else:
                effective_start = "2024-01-01"
                effective_end = None
                status = "effective"

            policy_content = (
                f"{title}. This is a fictional sample HR policy "
                f"for the HR Policy Intelligence project. "
                f"It describes eligibility, request procedures, "
                f"approvals, documentation, timelines and exceptions. "
                f"Employees should contact the HR department for "
                f"case-specific clarification."
            )

            connection.execute("""
                INSERT OR IGNORE INTO PolicyVersion (
                    policy_version_id,
                    policy_id,
                    version_number,
                    version_label,
                    effective_start,
                    effective_end,
                    audience,
                    status,
                    policy_content,
                    approved_by_employee_id,
                    approved_at,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                policy_id,
                version_number,
                f"Version {version_number}",
                effective_start,
                effective_end,
                "all_staff",
                status,
                policy_content,
                "EMP0118",
                f"{effective_start}T10:00:00",
                f"{effective_start}T09:00:00"
            ))

        current_version_id = f"{policy_id}-V{version_count}"

        for i, topic in enumerate(topics, start=1):
            article_id = f"KA-{policy_id}-{i:02d}"
            article_title = f"{title} - {topic}"

            answer = (
                f"This article explains {topic.lower()} "
                f"under the {title.lower()}. "
                f"Refer to the applicable policy version for "
                f"the complete requirements. For individual "
                f"exceptions or sensitive matters, contact HR."
            )

            connection.execute("""
                INSERT OR IGNORE INTO KnowledgeArticle (
                    knowledge_article_id,
                    policy_version_id,
                    title,
                    answer_snippet,
                    topic_tags,
                    audience,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article_id,
                current_version_id,
                article_title,
                answer,
                f'["{category}", "{topic.lower()}"]',
                "all_staff",
                1,
                "2026-01-01T10:00:00",
                now.isoformat()
            ))

    connection.commit()

    print("Policy data generated successfully!")

    for table in [
        "PolicyDocument",
        "PolicyVersion",
        "KnowledgeArticle"
    ]:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table}: {count}")

except sqlite3.Error as error:
    connection.rollback()
    print("Database error:", error)

finally:
    connection.close()
