
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "hr_policy.db"


def detect_anomalies():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    anomalies = []

    try:
        # ANOM-001: Obsolete policy citation
        obsolete_citations = connection.execute(
            """
            SELECT
                r.ticket_id,
                r.policy_version_id,
                p.version_label,
                p.status
            FROM Resolution r
            JOIN PolicyVersion p
                ON r.policy_version_id = p.policy_version_id
            WHERE p.status = 'superseded'
            """
        ).fetchall()

        for row in obsolete_citations:
            anomalies.append({
                "anomaly_id": "ANOM-001",
                "ticket_id": row["ticket_id"],
                "type": "obsolete_policy_citation",
                "severity": "high",
                "evidence": (
                    f"Resolution cites superseded policy version "
                    f"{row['policy_version_id']} ({row['version_label']})"
                )
            })

        # ANOM-002: Restricted ticket misrouting
        misrouted_tickets = connection.execute(
            """
            SELECT
                t.ticket_id,
                t.sensitivity,
                a.assigned_queue,
                a.assignment_status
            FROM Ticket t
            JOIN Assignment a
                ON t.ticket_id = a.ticket_id
            WHERE t.sensitivity = 'restricted'
              AND a.assigned_queue = 'HR_GENERAL'
            """
        ).fetchall()

        for row in misrouted_tickets:
            anomalies.append({
                "anomaly_id": "ANOM-002",
                "ticket_id": row["ticket_id"],
                "type": "sensitive_ticket_misrouting",
                "severity": "critical",
                "evidence": (
                    f"Restricted ticket was assigned to "
                    f"{row['assigned_queue']} "
                    f"(assignment status: {row['assignment_status']})"
                )
            })

        # ANOM-003: Invalid business-hours SLA
        invalid_slas = connection.execute(
            """
            SELECT
                sla_id,
                sla_name,
                business_days
            FROM SLA
            WHERE calendar_type = 'business_hours'
            """
        ).fetchall()

        for row in invalid_slas:
            try:
                business_days = json.loads(row["business_days"])
                valid_days = (
                    isinstance(business_days, list)
                    and len(business_days) > 0
                    and all(
                        isinstance(day, int) and 0 <= day <= 6
                        for day in business_days
                    )
                    and len(set(business_days)) == len(business_days)
                )
            except (json.JSONDecodeError, TypeError):
                valid_days = False

            if not valid_days:
                anomalies.append({
                    "anomaly_id": "ANOM-003",
                    "ticket_id": None,
                    "type": "invalid_sla_configuration",
                    "severity": "high",
                    "evidence": (
                        f"SLA {row['sla_id']} has invalid "
                        f"business days: {row['business_days']}"
                    )
                })

        # ANOM-004: Unsupported assistant claim
        assistant_messages = connection.execute(
            """
            SELECT
                ticket_id,
                message_text
            FROM Message
            WHERE sender_type = 'assistant'
            """
        ).fetchall()

        for row in assistant_messages:
            message = row["message_text"].lower()

            if (
                "guaranteed 30 days" in message
                and "annual leave" in message
            ):
                anomalies.append({
                    "anomaly_id": "ANOM-004",
                    "ticket_id": row["ticket_id"],
                    "type": "unsupported_policy_claim",
                    "severity": "critical",
                    "evidence": (
                        "Assistant claims 30 days of guaranteed "
                        "annual leave without policy support."
                    )
                })

        return anomalies

    finally:
        connection.close()


if __name__ == "__main__":
    results = detect_anomalies()

    print("\nANOMALY DETECTION RESULTS")
    print("=" * 60)

    for anomaly in results:
        print(f"\nAnomaly ID: {anomaly['anomaly_id']}")
        print(f"Ticket: {anomaly['ticket_id']}")
        print(f"Type: {anomaly['type']}")
        print(f"Severity: {anomaly['severity']}")
        print(f"Evidence: {anomaly['evidence']}")

    print("\n" + "=" * 60)
    print("Total anomalies detected:", len(results))
