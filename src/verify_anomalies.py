
import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

OPERATIONAL_DB = BASE_DIR / "data" / "hr_policy.db"
CLEAN_DB = BASE_DIR / "data" / "hr_policy_clean.db"
GROUND_TRUTH = BASE_DIR / "audit" / "anomaly_ground_truth.csv"

checks = []


def report(name, passed, details=""):
    checks.append(passed)
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {details}")


try:
    print("\nANOMALY VERIFICATION\n")

    with open(GROUND_TRUTH, newline="", encoding="utf-8") as file:
        labels = list(csv.DictReader(file))

    report(
        "Ground truth contains four anomalies",
        len(labels) == 4,
        len(labels)
    )

    expected_types = {
        "obsolete_policy_citation",
        "sensitive_case_misrouting",
        "incorrect_sla_business_hours",
        "unsupported_policy_claim"
    }

    actual_types = {item["anomaly_type"] for item in labels}

    report(
        "All four anomaly types are present",
        actual_types == expected_types,
        len(actual_types)
    )

    operational = sqlite3.connect(OPERATIONAL_DB)
    operational.execute("PRAGMA foreign_keys = ON")

    clean = sqlite3.connect(CLEAN_DB)

    print("\nOPERATIONAL DATABASE CHECKS\n")

    foreign_keys = operational.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    report(
        "Operational foreign-key integrity",
        len(foreign_keys) == 0,
        len(foreign_keys)
    )

    obsolete = operational.execute("""
        SELECT COUNT(*)
        FROM Resolution r
        JOIN PolicyVersion v
            ON r.policy_version_id = v.policy_version_id
        WHERE r.ticket_id = 'TKT00011'
          AND v.status = 'superseded'
    """).fetchone()[0]

    report(
        "Obsolete policy citation injected",
        obsolete == 1,
        obsolete
    )

    misrouted = operational.execute("""
        SELECT COUNT(*)
        FROM Ticket t
        JOIN Assignment a ON t.ticket_id = a.ticket_id
        WHERE t.ticket_id = 'TKT00006'
          AND t.sensitivity = 'restricted'
          AND a.assigned_queue = 'HR_GENERAL'
    """).fetchone()[0]

    report(
        "Restricted ticket misrouting injected",
        misrouted == 1,
        misrouted
    )

    bad_sla = operational.execute("""
        SELECT COUNT(*)
        FROM Ticket t
        JOIN SLA s ON t.sla_id = s.sla_id
        WHERE t.ticket_id = 'TKT00001'
          AND s.calendar_type = 'business_hours'
          AND s.business_days = '[]'
    """).fetchone()[0]

    report(
        "Incorrect business-hours SLA injected",
        bad_sla == 1,
        bad_sla
    )

    unsupported = operational.execute("""
        SELECT COUNT(*)
        FROM Message
        WHERE ticket_id = 'TKT00001'
          AND message_text LIKE '%30 days of annual leave%'
    """).fetchone()[0]

    report(
        "Unsupported policy claim injected",
        unsupported == 1,
        unsupported
    )

    print("\nCLEAN DATABASE CHECKS\n")

    clean_tickets = clean.execute(
        "SELECT COUNT(*) FROM Ticket"
    ).fetchone()[0]

    clean_assignments = clean.execute(
        "SELECT COUNT(*) FROM Assignment"
    ).fetchone()[0]

    clean_messages = clean.execute(
        "SELECT COUNT(*) FROM Message"
    ).fetchone()[0]

    report(
        "Clean database ticket count",
        clean_tickets == 5000,
        clean_tickets
    )

    report(
        "Clean database assignment count",
        clean_assignments == 5000,
        clean_assignments
    )

    report(
        "Clean database message count",
        clean_messages == 20000,
        clean_messages
    )

    clean_misrouting = clean.execute("""
        SELECT COUNT(*)
        FROM Ticket t
        JOIN Assignment a ON t.ticket_id = a.ticket_id
        WHERE t.ticket_id = 'TKT00006'
          AND t.sensitivity = 'restricted'
          AND a.assigned_queue = 'HR_GENERAL'
    """).fetchone()[0]

    report(
        "Clean database has no injected misrouting",
        clean_misrouting == 0,
        clean_misrouting
    )

    operational.close()
    clean.close()

    print("\nFINAL RESULT\n")

    passed = sum(checks)
    total = len(checks)

    print(f"Checks passed: {passed}/{total}")

    if passed == total:
        print("All anomaly verification checks passed!")
    else:
        print("Some checks failed. Review the results.")

except (sqlite3.Error, OSError, KeyError) as error:
    print("Verification error:", error)
