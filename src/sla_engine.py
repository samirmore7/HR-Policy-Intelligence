
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "hr_policy.db"


def get_sla(connection, ticket_id):
    return connection.execute(
        """
        SELECT
            s.sla_id,
            s.calendar_type,
            s.response_target_minutes,
            s.resolution_target_minutes,
            s.business_start_local,
            s.business_end_local,
            s.business_days,
            s.timezone
        FROM Ticket t
        JOIN SLA s ON t.sla_id = s.sla_id
        WHERE t.ticket_id = ?
        """,
        (ticket_id,)
    ).fetchone()


def add_business_minutes(
    start,
    minutes,
    business_start,
    business_end,
    business_days
):
    if not business_days:
        raise ValueError("SLA has no configured business days.")

    if business_start >= business_end:
        raise ValueError("Invalid business hours configuration.")

    current = start
    remaining = minutes

    while remaining > 0:
        if current.weekday() not in business_days:
            current = (current + timedelta(days=1)).replace(
                hour=business_start.hour,
                minute=business_start.minute,
                second=0,
                microsecond=0
            )
            continue

        opening = current.replace(
            hour=business_start.hour,
            minute=business_start.minute,
            second=0,
            microsecond=0
        )

        closing = current.replace(
            hour=business_end.hour,
            minute=business_end.minute,
            second=0,
            microsecond=0
        )

        if current < opening:
            current = opening

        if current >= closing:
            current = (current + timedelta(days=1)).replace(
                hour=business_start.hour,
                minute=business_start.minute,
                second=0,
                microsecond=0
            )
            continue

        available = int(
            (closing - current).total_seconds() / 60
        )

        consumed = min(remaining, available)

        current += timedelta(minutes=consumed)
        remaining -= consumed

    return current


def calculate_deadlines(ticket_id):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        ticket = connection.execute(
            """
            SELECT created_at
            FROM Ticket
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found.")

        sla = get_sla(connection, ticket_id)

        if not sla:
            raise ValueError(f"No SLA found for {ticket_id}.")

        timezone_name = sla["timezone"]
        tz = ZoneInfo(timezone_name)

        created_at = datetime.fromisoformat(
            ticket["created_at"]
        )

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=tz)
        else:
            created_at = created_at.astimezone(tz)

        if sla["calendar_type"] == "24x7":

            response_deadline = created_at + timedelta(
                minutes=sla["response_target_minutes"]
            )

            resolution_deadline = created_at + timedelta(
                minutes=sla["resolution_target_minutes"]
            )

        elif sla["calendar_type"] == "business_hours":

            business_start = time.fromisoformat(
                sla["business_start_local"]
            )

            business_end = time.fromisoformat(
                sla["business_end_local"]
            )

            business_days = set(
                json.loads(sla["business_days"])
            )

            response_deadline = add_business_minutes(
                created_at,
                sla["response_target_minutes"],
                business_start,
                business_end,
                business_days
            )

            resolution_deadline = add_business_minutes(
                created_at,
                sla["resolution_target_minutes"],
                business_start,
                business_end,
                business_days
            )

        else:
            raise ValueError(
                f"Unsupported SLA calendar: {sla['calendar_type']}"
            )

        return {
            "ticket_id": ticket_id,
            "sla_id": sla["sla_id"],
            "calendar_type": sla["calendar_type"],
            "response_deadline": response_deadline.isoformat(),
            "resolution_deadline": resolution_deadline.isoformat()
        }

    finally:
        connection.close()


def evaluate_sla(ticket_id):
    deadlines = calculate_deadlines(ticket_id)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        ticket = connection.execute(
            """
            SELECT first_response_at, resolved_at
            FROM Ticket
            WHERE ticket_id = ?
            """,
            (ticket_id,)
        ).fetchone()

        response_deadline = datetime.fromisoformat(
            deadlines["response_deadline"]
        )

        resolution_deadline = datetime.fromisoformat(
            deadlines["resolution_deadline"]
        )

        now = datetime.now(response_deadline.tzinfo)

        response_time = None
        resolution_time = None

        if ticket["first_response_at"]:
            response_time = datetime.fromisoformat(
                ticket["first_response_at"]
            )

            if response_time.tzinfo is None:
                response_time = response_time.replace(
                    tzinfo=response_deadline.tzinfo
                )
            else:
                response_time = response_time.astimezone(
                    response_deadline.tzinfo
                )

        if ticket["resolved_at"]:
            resolution_time = datetime.fromisoformat(
                ticket["resolved_at"]
            )

            if resolution_time.tzinfo is None:
                resolution_time = resolution_time.replace(
                    tzinfo=resolution_deadline.tzinfo
                )
            else:
                resolution_time = resolution_time.astimezone(
                    resolution_deadline.tzinfo
                )

        if response_time:
            response_status = (
                "met"
                if response_time <= response_deadline
                else "breached"
            )
        elif now > response_deadline:
            response_status = "breached"
        elif (
            response_deadline - now
        ).total_seconds() <= 3600:
            response_status = "at_risk"
        else:
            response_status = "within_sla"

        if resolution_time:
            resolution_status = (
                "met"
                if resolution_time <= resolution_deadline
                else "breached"
            )
        elif now > resolution_deadline:
            resolution_status = "breached"
        elif (
            resolution_deadline - now
        ).total_seconds() <= 3600:
            resolution_status = "at_risk"
        else:
            resolution_status = "within_sla"

        return {
            **deadlines,
            "response_status": response_status,
            "resolution_status": resolution_status
        }

    finally:
        connection.close()


def record_sla_breach(ticket_id):
    evaluation = evaluate_sla(ticket_id)

    breached = []

    if evaluation["response_status"] == "breached":
        breached.append("response")

    if evaluation["resolution_status"] == "breached":
        breached.append("resolution")

    if not breached:
        return {
            "ticket_id": ticket_id,
            "breach_recorded": False,
            "reason": "No SLA breach detected."
        }

    connection = sqlite3.connect(DB_PATH)

    try:
        existing_event = connection.execute(
            """
            SELECT event_id
            FROM TicketEvent
            WHERE ticket_id = ?
              AND event_type = 'sla_breached'
              AND json_extract(event_details, '$.source') = 'sla_engine'
            """,
            (ticket_id,)
        ).fetchone()

        if existing_event:
            return {
                "ticket_id": ticket_id,
                "breach_recorded": False,
                "reason": "SLA breach event already exists."
            }

        event_id = f"EVT-{__import__('uuid').uuid4().hex[:12]}"

        details = {
            "source": "sla_engine",
            "breached_slas": breached,
            "response_status": evaluation["response_status"],
            "resolution_status": evaluation["resolution_status"]
        }

        connection.execute(
            """
            INSERT INTO TicketEvent (
                event_id,
                ticket_id,
                event_type,
                actor_type,
                event_details,
                created_at
            )
            VALUES (?, ?, 'sla_breached', 'system', ?, ?)
            """,
            (
                event_id,
                ticket_id,
                json.dumps(details),
                datetime.now().astimezone().isoformat()
            )
        )

        connection.commit()

        return {
            "ticket_id": ticket_id,
            "breach_recorded": True,
            "breached_slas": breached,
            "event_id": event_id
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
