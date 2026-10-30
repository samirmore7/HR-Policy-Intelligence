
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(20261022)

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

now = datetime(2026, 10, 1, 10, 0, 0)

departments = [
    ("DEP001", "Human Resources", "HR"),
    ("DEP002", "Engineering", "ENG"),
    ("DEP003", "Finance", "FIN"),
    ("DEP004", "Marketing", "MKT"),
    ("DEP005", "Operations", "OPS"),
    ("DEP006", "Information Technology", "IT"),
]

try:
    for department_id, name, code in departments:
        connection.execute("""
            INSERT OR IGNORE INTO Department (
                department_id,
                department_name,
                department_code,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (department_id, name, code, now.isoformat()))

    employees = []

    for i in range(1, 101):
        department = random.choice(departments)

        employees.append({
            "employee_id": f"EMP{i:04d}",
            "department_id": department[0],
            "display_name": f"Employee {i:03d}",
            "employee_type": "employee",
            "audience": "all_staff",
            "employment_status": "active",
            "manager_employee_id": None,
        })

    for i in range(101, 111):
        department = departments[(i - 101) % len(departments)]

        employees.append({
            "employee_id": f"EMP{i:04d}",
            "department_id": department[0],
            "display_name": f"Manager {i - 100:02d}",
            "employee_type": "manager",
            "audience": "manager",
            "employment_status": "active",
            "manager_employee_id": None,
        })

    for i in range(111, 116):
        employees.append({
            "employee_id": f"EMP{i:04d}",
            "department_id": "DEP001",
            "display_name": f"HR Partner {i - 110:02d}",
            "employee_type": "hr_partner",
            "audience": "hr_only",
            "employment_status": "active",
            "manager_employee_id": "EMP0101",
        })

    for i in range(116, 118):
        employees.append({
            "employee_id": f"EMP{i:04d}",
            "department_id": "DEP006",
            "display_name": f"IT Operations {i - 115:02d}",
            "employee_type": "it_operations",
            "audience": "it_operations",
            "employment_status": "active",
            "manager_employee_id": "EMP0106",
        })

    employees.append({
        "employee_id": "EMP0118",
        "department_id": "DEP001",
        "display_name": "HR Administrator",
        "employee_type": "administrator",
        "audience": "hr_only",
        "employment_status": "active",
        "manager_employee_id": "EMP0101",
    })

    for employee in employees:
        start_date = now.date() - timedelta(
            days=random.randint(30, 2000)
        )

        connection.execute("""
            INSERT OR IGNORE INTO Employee (
                employee_id,
                department_id,
                employee_type,
                display_name,
                audience,
                employment_status,
                start_date,
                manager_employee_id,
                is_synthetic,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee["employee_id"],
            employee["department_id"],
            employee["employee_type"],
            employee["display_name"],
            employee["audience"],
            employee["employment_status"],
            start_date.isoformat(),
            employee["manager_employee_id"],
            1,
            now.isoformat()
        ))

    connection.commit()

    department_count = connection.execute(
        "SELECT COUNT(*) FROM Department"
    ).fetchone()[0]

    employee_count = connection.execute(
        "SELECT COUNT(*) FROM Employee"
    ).fetchone()[0]

    print("Synthetic data generated successfully!")
    print("Departments:", department_count)
    print("Employees:", employee_count)

except sqlite3.Error as error:
    connection.rollback()
    print("Database error:", error)

finally:
    connection.close()
