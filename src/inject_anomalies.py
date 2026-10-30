
import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"
CLEAN_DATABASE_PATH = BASE_DIR / "data" / "hr_policy_clean.db"
GROUND_TRUTH_PATH = BASE_DIR / "audit" / "anomaly_ground_truth.csv"

BASE_DIR.joinpath("audit").mkdir(exist_ok=True)

if GROUND_TRUTH_PATH.exists():
    print("Anomaly ground truth already exists.")
    print("Skipping injection to avoid duplicate changes.")
    raise SystemExit

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

anomalies = []

try:
    # Preserve the clean database before changing operational records.
    if not CLEAN_DATABASE_PATH.exists():
        clean_connection = sqlite3.connect(CLEAN_DATABASE_PATH)
        connection.backup(clean_connection)
        clean_connection.close()

    # 1. Obsolete policy citation
    obsolete_case = connection.execute("""
        SELECT
            r.resolution_id,
            r.ticket_id,
            d.policy_id
        FROM Resolution r
        JOIN PolicyVersion current_version
            ON r.policy_version_id = current_version.policy_version_id
        JOIN PolicyDocument d
            ON current_version.policy_id = d.policy_id
        WHERE r.resolution_type = 'policy_answer'
          AND current_version.status = 'effective'
          AND EXISTS (
              SELECT 1
              FROM PolicyVersion old_version
              WHERE old_version.policy_id = d.policy_id
                AND old_version.status = 'superseded'
          )
        ORDER BY r.ticket_id
        LIMIT 1
    """).fetchone()

    if not obsolete_case:
        raise ValueError("No suitable ticket found for obsolete policy anomaly.")

    resolution_id, ticket_id, policy_id = obsolete_case

    old_version_id = connection.execute("""
        SELECT policy_version_id
        FROM PolicyVersion
        WHERE policy_id = ?
          AND status = 'superseded'
        ORDER BY version_number
        LIMIT 1
    """, (policy_id,)).fetchone()[0]

    connection.execute("""
        UPDATE Resolution
        SET policy_version_id = ?
        WHERE resolution_id = ?
    """, (old_version_id, resolution_id))

    anomalies.append({
        "anomaly_id": "ANOM-001",
        "ticket_id": ticket_id,
        "anomaly_type": "obsolete_policy_citation",
        "injected_location": "Resolution.policy_version_id",
        "expected_behavior": "Use the currently effective policy version.",
        "injected_value": old_version_id
    })

    # 2. Sensitive ticket sent to the general queue
    sensitive_case = connection.execute("""
        SELECT t.ticket_id, a.assignment_id
        FROM Ticket t
        JOIN Assignment a ON t.ticket_id = a.ticket_id
        WHERE t.sensitivity = 'restricted'
          AND a.assigned_queue = 'HR_RESTRICTED'
        ORDER BY t.ticket_id
        LIMIT 1
    """).fetchone()

    if not sensitive_case:
        raise ValueError("No suitable restricted ticket found.")

    ticket_id, assignment_id = sensitive_case

    connection.execute("""
        UPDATE Assignment
        SET assigned_queue = 'HR_GENERAL',
            assignment_reason = 'General HR queue routing'
        WHERE assignment_id = ?
    """, (assignment_id,))

    anomalies.append({
        "anomaly_id": "ANOM-002",
        "ticket_id": ticket_id,
        "anomaly_type": "sensitive_case_misrouting",
        "injected_location": "Assignment.assigned_queue",
        "expected_behavior": "Route restricted cases to HR_RESTRICTED.",
        "injected_value": "HR_GENERAL"
    })

    # 3. SLA configuration excludes all required business days
    sla_case = connection.execute("""
        SELECT ticket_id, category_id, priority
        FROM Ticket
        WHERE sensitivity = 'normal'
        ORDER BY ticket_id
        LIMIT 1
    """).fetchone()

    if not sla_case:
        raise ValueError("No suitable ticket found for SLA anomaly.")

    ticket_id, category_id, priority = sla_case

    connection.execute("""
        INSERT INTO SLA (
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
        VALUES (
            'SLA-ANOMALY-001',
            'Anomalous SLA - No Business Days',
            ?,
            ?,
            'business_hours',
            60,
            1440,
            '09:00',
            '18:00',
            '[]',
            'Asia/Kolkata',
            '2026-01-01',
            NULL,
            1
        )
    """, (category_id, priority))

    connection.execute("""
        UPDATE Ticket
        SET sla_id = ?
        WHERE ticket_id = ?
    """, ("SLA-ANOMALY-001", ticket_id))

    anomalies.append({
        "anomaly_id": "ANOM-003",
        "ticket_id": ticket_id,
        "anomaly_type": "incorrect_sla_business_hours",
        "injected_location": "SLA.business_days",
        "expected_behavior": "Include Monday to Friday as business days.",
        "injected_value": "[]"
    })

    # 4. Unsupported policy claim in an assistant response
    unsupported_case = connection.execute("""
        SELECT m.message_id, m.ticket_id
        FROM Message m
        JOIN Ticket t ON m.ticket_id = t.ticket_id
        WHERE m.sender_type = 'assistant'
          AND m.is_internal = 0
          AND t.sensitivity = 'normal'
        ORDER BY m.ticket_id, m.sequence_number
        LIMIT 1
    """).fetchone()

    if not unsupported_case:
        raise ValueError("No suitable assistant message found.")

    message_id, ticket_id = unsupported_case

    unsupported_claim = (
        "All employees are guaranteed 30 days of annual leave "
        "regardless of their employment type or tenure."
    )

    connection.execute("""
        UPDATE Message
        SET message_text = ?
        WHERE message_id = ?
    """, (unsupported_claim, message_id))

    anomalies.append({
        "anomaly_id": "ANOM-004",
        "ticket_id": ticket_id,
        "anomaly_type": "unsupported_policy_claim",
        "injected_location": "Message.message_text",
        "expected_behavior": "Only present claims supported by an effective policy.",
        "injected_value": unsupported_claim
    })

    connection.commit()

    # Keep ground-truth labels outside the operational database.
    with open(
        GROUND_TRUTH_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "anomaly_id",
                "ticket_id",
                "anomaly_type",
                "injected_location",
                "expected_behavior",
                "injected_value"
            ]
        )

        writer.writeheader()
        writer.writerows(anomalies)

    print("Anomaly injection completed successfully!")
    print("Anomalies injected:", len(anomalies))
    print("Clean database:", CLEAN_DATABASE_PATH)
    print("Ground truth:", GROUND_TRUTH_PATH)

    print("\nInjected anomalies:")

    for anomaly in anomalies:
        print(
            anomaly["anomaly_id"],
            anomaly["anomaly_type"],
            anomaly["ticket_id"]
        )

except (sqlite3.Error, ValueError, OSError) as error:
    connection.rollback()
    print("Anomaly injection failed:", error)

finally:
    connection.close()
