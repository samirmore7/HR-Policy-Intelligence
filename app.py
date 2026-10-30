
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "hr_policy.db"

st.set_page_config(
    page_title="PeopleOps Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEMES = {
    "Midnight": ["#0B1020", "#111A2E", "#17233B", "#EDF2FF", "#9AA8C7", "#263653", "#8B9CFF", "#52D6C8"],
    "Light": ["#F4F6FB", "#FFFFFF", "#F0F3FA", "#18233A", "#697792", "#E1E6F0", "#5969D9", "#159D91"],
    "Ocean": ["#071B2A", "#0D2A3D", "#12384D", "#E8F7FC", "#9BBBC9", "#1D4B60", "#55B8E8", "#54D6C0"],
    "Forest": ["#101D19", "#192B24", "#21382E", "#EDF7F0", "#A7BBAE", "#345044", "#9BCB8A", "#62D6B0"],
}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Midnight"


def apply_theme(name):
    bg, surface, surface2, text, muted, border, accent, accent2 = THEMES[name]

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {{
        --bg:{bg};
        --surface:{surface};
        --surface2:{surface2};
        --text:{text};
        --muted:{muted};
        --border:{border};
        --accent:{accent};
        --accent2:{accent2};
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background:var(--bg);
        color:var(--text);
        font-family:'DM Sans',sans-serif;
    }}

    [data-testid="stHeader"] {{
        background:transparent;
    }}

    [data-testid="stSidebar"] {{
        background:{surface};
        border-right:1px solid var(--border);
    }}

    h1, h2, h3, h4 {{
        font-family:'Manrope',sans-serif !important;
        color:var(--text) !important;
        letter-spacing:-.035em;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] p {{
        color:var(--muted);
    }}

    [data-testid="stMetric"] {{
        background:var(--surface);
        border:1px solid var(--border);
        padding:17px 19px;
        border-radius:16px;
    }}

    [data-testid="stMetricLabel"] {{
        color:var(--muted) !important;
    }}

    [data-testid="stMetricValue"] {{
        color:var(--text) !important;
        font-family:'Manrope',sans-serif;
        font-weight:800;
    }}

    .hero {{
        background:
            radial-gradient(circle at 90% 5%,{accent}30,transparent 35%),
            linear-gradient(120deg,var(--surface),var(--surface2));
        border:1px solid var(--border);
        border-radius:22px;
        padding:28px 30px;
        margin:4px 0 22px;
    }}

    .kicker {{
        color:var(--accent2);
        text-transform:uppercase;
        font-size:11px;
        letter-spacing:.16em;
        font-weight:800;
        margin-bottom:10px;
    }}

    .hero-title {{
        color:var(--text);
        font-family:'Manrope',sans-serif;
        font-size:clamp(27px,3vw,39px);
        line-height:1.12;
        font-weight:800;
        letter-spacing:-.045em;
        margin-bottom:10px;
    }}

    .hero-copy {{
        color:var(--muted);
        max-width:760px;
        font-size:14px;
        line-height:1.65;
    }}

    .section-label {{
        color:var(--accent2);
        font-size:11px;
        text-transform:uppercase;
        letter-spacing:.14em;
        font-weight:800;
        margin:18px 0 9px;
    }}

    .panel {{
        background:var(--surface);
        border:1px solid var(--border);
        border-radius:16px;
        padding:18px 20px;
        margin-bottom:14px;
    }}

    .panel-title {{
        color:var(--text);
        font-family:'Manrope',sans-serif;
        font-weight:750;
        font-size:16px;
    }}

    .muted {{
        color:var(--muted);
        font-size:12px;
    }}

    .brand-mark {{
        display:inline-flex;
        width:36px;
        height:36px;
        align-items:center;
        justify-content:center;
        border-radius:12px;
        background:linear-gradient(135deg,var(--accent),var(--accent2));
        color:#10172b;
        font-weight:900;
        font-size:19px;
        margin-right:9px;
    }}

    .brand-name {{
        font-family:'Manrope',sans-serif;
        font-size:17px;
        font-weight:800;
        color:var(--text);
        vertical-align:middle;
    }}

    div[data-testid="stButton"]>button {{
        border-radius:11px;
        border:1px solid var(--border);
        background:var(--surface2);
        color:var(--text);
        font-weight:650;
        min-height:41px;
    }}

    div[data-testid="stButton"]>button:hover {{
        border-color:var(--accent);
        color:var(--accent);
    }}

    div[data-testid="stButton"]>button[kind="primary"] {{
        background:var(--accent);
        border-color:var(--accent);
        color:#10172b;
    }}

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {{
        background:var(--surface);
        color:var(--text);
        border-color:var(--border);
        border-radius:10px;
    }}

    [data-testid="stDataFrame"] {{
        border:1px solid var(--border);
        border-radius:12px;
        overflow:hidden;
    }}

    hr {{
        border-color:var(--border);
    }}

    #MainMenu, footer {{
        visibility:hidden;
    }}

    .block-container {{
        padding-top:2rem;
        padding-bottom:3rem;
        max-width:1500px;
    }}
    </style>
    """, unsafe_allow_html=True)


apply_theme(st.session_state.theme_name)


# Database functions

def db():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def read_df(sql, params=()):
    with db() as con:
        return pd.read_sql_query(sql, con, params=params)


def count(sql):
    with db() as con:
        return con.execute(sql).fetchone()[0]


def hero(kicker, title, copy):
    st.markdown(
        f'<div class="hero">'
        f'<div class="kicker">{kicker}</div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-copy">{copy}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def error_box(error):
    st.error(str(error))
    st.caption("Check that the database and required project modules are available.")


# Sidebar

with st.sidebar:
    st.markdown(
        '<div style="padding:8px 4px 20px">'
        '<span class="brand-mark">✦</span>'
        '<span class="brand-name">PeopleOps AI</span>'
        '<div class="muted" style="margin:9px 0 0 2px">'
        'HR intelligence workspace</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-label">Workspace</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "HR Assistant",
            "Ticket Explorer",
            "SLA Command Center",
            "Anomaly Intelligence",
            "Policy Library"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        '<div class="section-label">Appearance</div>',
        unsafe_allow_html=True
    )

    theme_name = st.selectbox(
        "Theme",
        list(THEMES),
        index=list(THEMES).index(st.session_state.theme_name),
        label_visibility="collapsed"
    )

    if theme_name != st.session_state.theme_name:
        st.session_state.theme_name = theme_name
        st.rerun()

    st.divider()

    st.markdown(
        '<div class="muted"><b>YottaFlex AI Challenge</b><br>'
        'Synthetic HR service desk<br>'
        'Local development environment</div>',
        unsafe_allow_html=True
    )


# Overview

if page == "Overview":

    hero(
        "People operations · intelligence",
        "A clearer view of every employee request.",
        "One workspace for policy-grounded answers, service operations, "
        "SLA visibility and proactive risk detection."
    )

    try:
        values = [
            count("SELECT COUNT(*) FROM Ticket"),
            count("SELECT COUNT(*) FROM Ticket WHERE status NOT IN ('resolved','closed')"),
            count("SELECT COUNT(*) FROM KnowledgeArticle"),
            count("SELECT COUNT(*) FROM Message"),
            count("SELECT COUNT(*) FROM Ticket WHERE status='escalated'"),
        ]

        cols = st.columns(5)

        for col, label, value in zip(
            cols,
            ["Tickets", "Open workload", "Policy articles", "Messages", "Escalated"],
            values
        ):
            col.metric(label, f"{value:,}")

        try:
            from src.anomaly_detector import detect_anomalies
            risks = len(detect_anomalies())
        except Exception:
            risks = 0

        st.metric("Detected anomalies", risks)

        left, right = st.columns([1.1, .9])

        with left:
            st.markdown(
                '<div class="section-label">Ticket volume by status</div>',
                unsafe_allow_html=True
            )

            data = read_df(
                "SELECT status, COUNT(*) AS tickets "
                "FROM Ticket GROUP BY status ORDER BY tickets DESC"
            )

            if not data.empty:
                st.bar_chart(data.set_index("status"), height=280)

        with right:
            st.markdown(
                '<div class="section-label">Requests by category</div>',
                unsafe_allow_html=True
            )

            data = read_df("""
                SELECT c.category_name, COUNT(t.ticket_id) AS tickets
                FROM Category c
                LEFT JOIN Ticket t ON t.category_id=c.category_id
                GROUP BY c.category_id,c.category_name
                ORDER BY tickets DESC
            """)

            st.dataframe(data, use_container_width=True, hide_index=True)

        st.markdown(
            '<div class="section-label">Recent tickets</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            read_df(
                "SELECT ticket_id,subject,category_id,status,sensitivity,created_at "
                "FROM Ticket ORDER BY created_at DESC LIMIT 10"
            ),
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        error_box(e)


# HR Assistant

elif page == "HR Assistant":

    hero(
        "Policy intelligence · conversational support",
        "Ask HR. Get answers grounded in policy.",
        "Routine questions use retrieved policy context. Sensitive topics "
        "are routed for human handling."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    try:
        tickets = read_df(
            "SELECT ticket_id FROM Ticket ORDER BY ticket_id LIMIT 500"
        )["ticket_id"].tolist()
    except Exception:
        tickets = []

    ticket_choice = st.selectbox(
        "Link a ticket (optional)",
        ["No linked ticket"] + tickets
    )

    question = st.text_area(
        "Your question",
        placeholder="What is the process for requesting annual leave?",
        height=110
    )

    c1, c2 = st.columns([1, 5])

    with c1:
        ask = st.button(
            "Ask assistant",
            type="primary",
            use_container_width=True
        )

    with c2:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()

    if ask:
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                from rag.assistant import HRPolicyAssistant

                if "assistant" not in st.session_state:
                    st.session_state.assistant = HRPolicyAssistant()

                ticket_id = (
                    None
                    if ticket_choice == "No linked ticket"
                    else ticket_choice
                )

                with st.spinner("Reviewing the request and policy sources..."):
                    result = st.session_state.assistant.ask(
                        question.strip(),
                        ticket_id=ticket_id
                    )

                st.session_state.chat_history.append({
                    "question": question.strip(),
                    "result": result
                })

            except Exception as e:
                error_box(e)

    for item in reversed(st.session_state.chat_history):
        st.markdown("**You**")
        st.write(item["question"])

        result = item["result"]

        if isinstance(result, dict):
            if result.get("escalated") or result.get("requires_human"):
                st.warning(
                    result.get(
                        "answer",
                        "This request requires human HR support."
                    )
                )
            else:
                st.markdown("**PeopleOps AI**")
                st.write(result.get("answer", result))

            sources = result.get("sources", [])

            if sources:
                with st.expander("Policy sources"):
                    for source in sources:
                        st.write(source)
        else:
            st.write(result)

        st.divider()


# Ticket Explorer

elif page == "Ticket Explorer":

    hero(
        "Service desk · case management",
        "Explore the employee support queue.",
        "Search synthetic tickets, inspect status and review "
        "employee-visible conversation history."
    )

    try:
        statuses = read_df(
            "SELECT DISTINCT status FROM Ticket ORDER BY status"
        )["status"].dropna().tolist()

        status = st.selectbox(
            "Status",
            ["All statuses"] + statuses
        )

        search = st.text_input(
            "Search ticket ID or subject",
            placeholder="TKT00001"
        )

        sql = """
            SELECT ticket_id,subject,category_id,status,sensitivity,created_at
            FROM Ticket
            WHERE 1=1
        """

        params = []

        if status != "All statuses":
            sql += " AND status=?"
            params.append(status)

        if search.strip():
            sql += " AND (ticket_id LIKE ? OR subject LIKE ?)"
            params.extend([
                f"%{search.strip()}%",
                f"%{search.strip()}%"
            ])

        sql += " ORDER BY created_at DESC LIMIT 300"

        tickets = read_df(sql, tuple(params))

        st.caption(f"{len(tickets)} tickets shown")

        st.dataframe(
            tickets,
            use_container_width=True,
            hide_index=True
        )

        if not tickets.empty:
            chosen = st.selectbox(
                "Open ticket",
                tickets.ticket_id.tolist()
            )

            st.markdown(
                '<div class="section-label">Ticket details</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                read_df(
                    "SELECT * FROM Ticket WHERE ticket_id=?",
                    (chosen,)
                ),
                use_container_width=True,
                hide_index=True
            )

            st.markdown(
                '<div class="section-label">Assignment history</div>',
                unsafe_allow_html=True
            )

            st.dataframe(
                read_df(
                    """
                    SELECT assigned_queue,assignment_status,assignment_reason,
                           assigned_at,ended_at
                    FROM Assignment
                    WHERE ticket_id=?
                    ORDER BY assigned_at
                    """,
                    (chosen,)
                ),
                use_container_width=True,
                hide_index=True
            )

            st.markdown(
                '<div class="section-label">Employee-visible conversation</div>',
                unsafe_allow_html=True
            )

            messages = read_df(
                """
                SELECT sender_type,message_text,created_at
                FROM Message
                WHERE ticket_id=? AND is_internal=0
                ORDER BY created_at
                """,
                (chosen,)
            )

            for _, msg in messages.iterrows():
                with st.chat_message(
                    "assistant"
                    if msg.sender_type == "assistant"
                    else "user"
                ):
                    st.caption(
                        f"{str(msg.sender_type).title()} · {msg.created_at}"
                    )
                    st.write(msg.message_text)

    except Exception as e:
        error_box(e)


# SLA Command Center

elif page == "SLA Command Center":

    hero(
        "Service performance · SLA monitoring",
        "Know which commitments need attention.",
        "Inspect response and resolution targets, evaluate individual "
        "tickets and record breach events."
    )

    try:
        from src.sla_engine import (
            calculate_deadlines,
            evaluate_sla,
            record_sla_breach
        )

        ids = read_df(
            "SELECT ticket_id FROM Ticket ORDER BY created_at DESC LIMIT 300"
        )["ticket_id"].tolist()

        if ids:
            chosen = st.selectbox("Select ticket", ids)

            deadlines = calculate_deadlines(chosen)
            evaluation = evaluate_sla(chosen)

            c1, c2 = st.columns(2)

            c1.metric(
                "First response deadline",
                str(deadlines.get("response_deadline", "Unavailable"))
            )

            c2.metric(
                "Resolution deadline",
                str(deadlines.get("resolution_deadline", "Unavailable"))
            )

            st.markdown(
                '<div class="section-label">SLA evaluation</div>',
                unsafe_allow_html=True
            )

            st.json(evaluation)

            if st.button("Record SLA breach event", type="primary"):
                if record_sla_breach(chosen):
                    st.success("SLA breach event recorded.")
                else:
                    st.info("No new breach event recorded.")

        st.markdown(
            '<div class="section-label">Ticket SLA inventory</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            read_df(
                """
                SELECT ticket_id,status,created_at,first_response_at,resolved_at
                FROM Ticket
                ORDER BY created_at DESC
                LIMIT 100
                """
            ),
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        error_box(e)


# Anomaly Intelligence

elif page == "Anomaly Intelligence":

    hero(
        "Trust & safety · data quality",
        "Surface risks before they become incidents.",
        "Rule-based checks inspect policy citations, restricted-case routing, "
        "SLA setup and unsupported assistant claims."
    )

    try:
        from src.anomaly_detector import detect_anomalies

        if st.button("Run anomaly scan", type="primary"):
            st.session_state.anomaly_results = detect_anomalies()

        results = st.session_state.get("anomaly_results")

        if results is None:
            results = detect_anomalies()

        critical = sum(
            x["severity"] == "critical"
            for x in results
        )

        high = sum(
            x["severity"] == "high"
            for x in results
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("Findings", len(results))
        c2.metric("Critical", critical)
        c3.metric("High", high)

        if results:
            st.dataframe(
                pd.DataFrame(results),
                use_container_width=True,
                hide_index=True
            )

            for item in results:
                with st.expander(
                    f"{item['anomaly_id']} · {item['type']} · "
                    f"{item['severity'].upper()}"
                ):
                    st.write(item["evidence"])
                    st.caption(
                        f"Ticket: {item.get('ticket_id') or 'SLA configuration'}"
                    )
        else:
            st.success("No anomalies detected by current rules.")

        truth_path = BASE_DIR / "audit" / "anomaly_ground_truth.csv"

        if truth_path.exists():
            truth = pd.read_csv(truth_path)

            expected = set(truth.anomaly_id.dropna())
            found = {x["anomaly_id"] for x in results}

            tp = len(expected & found)
            fp = len(found - expected)
            fn = len(expected - found)

            precision = tp / (tp + fp) if tp + fp else 0
            recall = tp / (tp + fn) if tp + fn else 0

            f1 = (
                2 * precision * recall / (precision + recall)
                if precision + recall
                else 0
            )

            st.markdown(
                '<div class="section-label">Ground-truth evaluation</div>',
                unsafe_allow_html=True
            )

            a, b, c = st.columns(3)

            a.metric("Precision", f"{precision:.1%}")
            b.metric("Recall", f"{recall:.1%}")
            c.metric("F1-score", f"{f1:.1%}")

            st.caption(
                "Scores measure detection of the four injected anomalies, "
                "not generalization to unseen cases."
            )

    except Exception as e:
        error_box(e)


# Policy Library

elif page == "Policy Library":

    hero(
        "Knowledge management · policy sources",
        "A searchable policy knowledge base.",
        "Inspect policy versions and article content used by the retrieval pipeline."
    )

    try:
        policies = read_df("""
            SELECT
                pd.policy_id,
                pd.title,
                pv.version_label,
                pv.status,
                pv.effective_from,
                pv.effective_to,
                pv.content
            FROM PolicyDocument pd
            JOIN PolicyVersion pv
                ON pd.policy_id=pv.policy_id
            ORDER BY pd.title,pv.effective_from DESC
        """)

        search = st.text_input(
            "Search policies",
            placeholder="Leave, payroll, benefits..."
        )

        if search.strip():
            mask = (
                policies.title.fillna("").str.contains(search, case=False)
                | policies.content.fillna("").str.contains(search, case=False)
            )
            policies = policies[mask]

        statuses = ["All versions"] + sorted(
            policies.status.dropna().unique().tolist()
        )

        selected = st.selectbox("Version status", statuses)

        if selected != "All versions":
            policies = policies[policies.status == selected]

        st.caption(f"{len(policies)} policy versions")

        for _, policy in policies.iterrows():
            with st.expander(
                f"{policy.title} · {policy.version_label} · {policy.status}"
            ):
                st.caption(
                    f"Effective from: {policy.effective_from} · "
                    f"Effective to: {policy.effective_to or 'Current'}"
                )
                st.write(policy.content)

    except Exception as e:
        error_box(e)
