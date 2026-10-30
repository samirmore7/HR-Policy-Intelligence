
import shutil
import sqlite3
from pathlib import Path

from . import sla_engine

BASE_DIR = Path(__file__).parent.parent
SOURCE_DB = BASE_DIR / "data" / "hr_policy.db"
TEST_DB = BASE_DIR / "data" / "sla_test.db"


def main():
    if TEST_DB.exists():
        TEST_DB.unlink()

    shutil.copy2(SOURCE_DB, TEST_DB)

    sla_engine.DB_PATH = TEST_DB

    try:
        ticket_ids = ["TKT00002", "TKT00003"]

        for ticket_id in ticket_ids:
            print("\n" + "=" * 50)
            print("Ticket:", ticket_id)

            deadlines = sla_engine.calculate_deadlines(ticket_id)

            print("\nDeadlines:")

            for key, value in deadlines.items():
                print(f"{key}: {value}")

            evaluation = sla_engine.evaluate_sla(ticket_id)

            print("\nSLA Evaluation:")
            print("Response Status:", evaluation["response_status"])
            print("Resolution Status:", evaluation["resolution_status"])

            result = sla_engine.record_sla_breach(ticket_id)

            print("\nBreach Recording:")
            print(result)

            second_result = sla_engine.record_sla_breach(ticket_id)

            print("\nDuplicate Check:")
            print(second_result)

            if evaluation["response_status"] == "breached" or \
               evaluation["resolution_status"] == "breached":
                assert result["breach_recorded"] is True
                assert second_result["breach_recorded"] is False
            else:
                assert result["breach_recorded"] is False

        connection = sqlite3.connect(TEST_DB)

        events = connection.execute(
            """
            SELECT ticket_id, event_type, event_details
            FROM TicketEvent
            WHERE event_type = 'sla_breached'
              AND json_extract(event_details, '$.source') = 'sla_engine'
            """
        ).fetchall()

        connection.close()

        print("\nRecorded SLA Breach Events:")

        for event in events:
            print(event)

        assert len(events) == 2

        print("\nAll SLA engine tests passed.")

    finally:
        if TEST_DB.exists():
            TEST_DB.unlink()


if __name__ == "__main__":
    main()
