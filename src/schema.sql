PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Department (
    department_id TEXT PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    department_code TEXT NOT NULL UNIQUE,
    manager_employee_id TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Employee (
    employee_id TEXT PRIMARY KEY,
    department_id TEXT NOT NULL,
    employee_type TEXT NOT NULL
        CHECK (employee_type IN (
            'employee',
            'manager',
            'hr_partner',
            'it_operations',
            'administrator',
            'candidate'
        )),
    display_name TEXT NOT NULL,
    audience TEXT NOT NULL
        CHECK (audience IN (
            'all_staff',
            'manager',
            'hr_only',
            'it_operations',
            'candidate'
        )),
    employment_status TEXT NOT NULL
        CHECK (employment_status IN (
            'preboarding',
            'active',
            'on_leave',
            'terminated',
            'candidate'
        )),
    start_date TEXT,
    end_date TEXT,
    manager_employee_id TEXT,
    is_synthetic INTEGER NOT NULL DEFAULT 1
        CHECK (is_synthetic IN (0, 1)),
    created_at TEXT NOT NULL,

    FOREIGN KEY (department_id)
        REFERENCES Department(department_id),

    FOREIGN KEY (manager_employee_id)
        REFERENCES Employee(employee_id),

    CHECK (
        start_date IS NULL
        OR end_date IS NULL
        OR date(end_date) >= date(start_date)
    )
);


CREATE TABLE IF NOT EXISTS PolicyDocument (
    policy_id TEXT PRIMARY KEY,
    policy_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category_code TEXT NOT NULL
        CHECK (category_code IN (
            'benefits',
            'leave',
            'payroll',
            'onboarding',
            'employee_relations',
            'general'
        )),
    owner_department_id TEXT NOT NULL,
    description TEXT,
    lifecycle_state TEXT NOT NULL DEFAULT 'draft'
        CHECK (lifecycle_state IN (
            'draft',
            'published',
            'retired'
        )),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (owner_department_id)
        REFERENCES Department(department_id),

    CHECK (date(updated_at) >= date(created_at))
);


CREATE TABLE IF NOT EXISTS PolicyVersion (
    policy_version_id TEXT PRIMARY KEY,
    policy_id TEXT NOT NULL,
    version_number INTEGER NOT NULL
        CHECK (version_number >= 1),
    version_label TEXT NOT NULL,
    effective_start TEXT NOT NULL,
    effective_end TEXT,
    audience TEXT NOT NULL
        CHECK (audience IN (
            'all_staff',
            'manager',
            'hr_only',
            'it_operations',
            'candidate'
        )),
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN (
            'draft',
            'effective',
            'superseded',
            'withdrawn'
        )),
    policy_content TEXT NOT NULL,
    approved_by_employee_id TEXT,
    approved_at TEXT,
    created_at TEXT NOT NULL,

    UNIQUE (policy_id, version_number),

    FOREIGN KEY (policy_id)
        REFERENCES PolicyDocument(policy_id),

    FOREIGN KEY (approved_by_employee_id)
        REFERENCES Employee(employee_id),

    CHECK (
        effective_end IS NULL
        OR date(effective_end) >= date(effective_start)
    ),

    CHECK (
        status = 'draft'
        OR approved_at IS NOT NULL
    )
);


CREATE TABLE IF NOT EXISTS KnowledgeArticle (
    knowledge_article_id TEXT PRIMARY KEY,
    policy_version_id TEXT NOT NULL,
    title TEXT NOT NULL,
    answer_snippet TEXT NOT NULL,
    topic_tags TEXT NOT NULL DEFAULT '[]',
    audience TEXT NOT NULL
        CHECK (audience IN (
            'all_staff',
            'manager',
            'hr_only',
            'it_operations',
            'candidate'
        )),
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    UNIQUE (policy_version_id, title),

    FOREIGN KEY (policy_version_id)
        REFERENCES PolicyVersion(policy_version_id),

    CHECK (length(trim(title)) > 0),
    CHECK (length(trim(answer_snippet)) > 0),
    CHECK (date(updated_at) >= date(created_at))
);

CREATE TABLE IF NOT EXISTS Category (
    category_id TEXT PRIMARY KEY,
    category_code TEXT NOT NULL UNIQUE
        CHECK (category_code IN (
            'benefits',
            'leave',
            'payroll',
            'onboarding',
            'employee_relations',
            'general'
        )),
    category_name TEXT NOT NULL UNIQUE,
    default_queue TEXT NOT NULL,
    default_priority TEXT NOT NULL
        CHECK (default_priority IN (
            'low',
            'normal',
            'high',
            'urgent'
        )),
    default_response_minutes INTEGER NOT NULL
        CHECK (default_response_minutes > 0),
    default_resolution_minutes INTEGER NOT NULL
        CHECK (default_resolution_minutes > 0),
    requires_restricted_handling INTEGER NOT NULL DEFAULT 0
        CHECK (requires_restricted_handling IN (0, 1)),
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS SLA (
    sla_id TEXT PRIMARY KEY,
    sla_name TEXT NOT NULL UNIQUE,
    category_id TEXT NOT NULL,
    priority TEXT NOT NULL
        CHECK (priority IN (
            'low',
            'normal',
            'high',
            'urgent'
        )),
    calendar_type TEXT NOT NULL
        CHECK (calendar_type IN (
            '24x7',
            'business_hours'
        )),
    response_target_minutes INTEGER NOT NULL
        CHECK (response_target_minutes > 0),
    resolution_target_minutes INTEGER NOT NULL
        CHECK (resolution_target_minutes > 0),
    business_start_local TEXT,
    business_end_local TEXT,
    business_days TEXT NOT NULL DEFAULT '[1,2,3,4,5]',
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    effective_start TEXT NOT NULL,
    effective_end TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    FOREIGN KEY (category_id)
        REFERENCES Category(category_id),

    CHECK (
        effective_end IS NULL
        OR date(effective_end) >= date(effective_start)
    ),

    CHECK (
        calendar_type = '24x7'
        OR (
            business_start_local IS NOT NULL
            AND business_end_local IS NOT NULL
        )
    )
);

CREATE TABLE IF NOT EXISTS Ticket (
    ticket_id TEXT PRIMARY KEY,
    requester_employee_id TEXT NOT NULL,
    category_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    initial_question TEXT NOT NULL,
    priority TEXT NOT NULL
        CHECK (priority IN (
            'low',
            'normal',
            'high',
            'urgent'
        )),
    sensitivity TEXT NOT NULL
        CHECK (sensitivity IN (
            'normal',
            'confidential',
            'restricted'
        )),
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN (
            'new',
            'triaged',
            'awaiting_clarification',
            'assigned',
            'in_progress',
            'escalated',
            'resolved',
            'closed',
            'reopened'
        )),
    channel TEXT NOT NULL
        CHECK (channel IN (
            'portal',
            'email',
            'chat',
            'api'
        )),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    first_response_at TEXT,
    resolved_at TEXT,
    closed_at TEXT,
    sla_id TEXT NOT NULL,

    FOREIGN KEY (requester_employee_id)
        REFERENCES Employee(employee_id),

    FOREIGN KEY (category_id)
        REFERENCES Category(category_id),

    FOREIGN KEY (sla_id)
        REFERENCES SLA(sla_id),

    CHECK (date(updated_at) >= date(created_at)),

    CHECK (
        first_response_at IS NULL
        OR datetime(first_response_at) >= datetime(created_at)
    ),

    CHECK (
        resolved_at IS NULL
        OR datetime(resolved_at) >= datetime(created_at)
    ),

    CHECK (
        closed_at IS NULL
        OR datetime(closed_at) >= datetime(created_at)
    ),

    CHECK (
        status NOT IN ('resolved', 'closed')
        OR resolved_at IS NOT NULL
    )
);

CREATE TABLE IF NOT EXISTS Message (
    message_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL
        CHECK (sequence_number >= 1),
    sender_type TEXT NOT NULL
        CHECK (sender_type IN (
            'employee',
            'assistant',
            'hr_agent',
            'system'
        )),
    sender_employee_id TEXT,
    message_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_internal INTEGER NOT NULL DEFAULT 0
        CHECK (is_internal IN (0, 1)),

    UNIQUE (ticket_id, sequence_number),

    FOREIGN KEY (ticket_id)
        REFERENCES Ticket(ticket_id),

    FOREIGN KEY (sender_employee_id)
        REFERENCES Employee(employee_id),

    CHECK (length(trim(message_text)) > 0),

    CHECK (
        sender_type IN ('assistant', 'system')
        OR sender_employee_id IS NOT NULL
    )
);

CREATE TABLE IF NOT EXISTS Assignment (
    assignment_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    assigned_queue TEXT NOT NULL,
    assigned_employee_id TEXT,
    assignment_status TEXT NOT NULL DEFAULT 'active'
        CHECK (assignment_status IN (
            'active',
            'reassigned',
            'completed',
            'cancelled'
        )),
    assignment_reason TEXT,
    assigned_at TEXT NOT NULL,
    ended_at TEXT,

    FOREIGN KEY (ticket_id)
        REFERENCES Ticket(ticket_id),

    FOREIGN KEY (assigned_employee_id)
        REFERENCES Employee(employee_id),

    CHECK (
        ended_at IS NULL
        OR datetime(ended_at) >= datetime(assigned_at)
    ),

    CHECK (
        assignment_status != 'active'
        OR ended_at IS NULL
    )
);

CREATE TABLE IF NOT EXISTS Resolution (
    resolution_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL UNIQUE,
    resolution_type TEXT NOT NULL
        CHECK (resolution_type IN (
            'policy_answer',
            'hr_handoff',
            'clarification',
            'manual_resolution',
            'unresolved'
        )),
    resolution_summary TEXT NOT NULL,
    confidence_score REAL
        CHECK (
            confidence_score IS NULL
            OR confidence_score BETWEEN 0 AND 1
        ),
    policy_version_id TEXT,
    knowledge_article_id TEXT,
    resolved_by_type TEXT NOT NULL
        CHECK (resolved_by_type IN (
            'assistant',
            'hr_agent',
            'system'
        )),
    resolved_by_employee_id TEXT,
    resolved_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES Ticket(ticket_id),

    FOREIGN KEY (policy_version_id)
        REFERENCES PolicyVersion(policy_version_id),

    FOREIGN KEY (knowledge_article_id)
        REFERENCES KnowledgeArticle(knowledge_article_id),

    FOREIGN KEY (resolved_by_employee_id)
        REFERENCES Employee(employee_id),

    CHECK (
        resolved_by_type = 'assistant'
        OR resolved_by_employee_id IS NOT NULL
    ),

    CHECK (
        resolution_type != 'policy_answer'
        OR (
            policy_version_id IS NOT NULL
            AND knowledge_article_id IS NOT NULL
        )
    )
);

CREATE TABLE IF NOT EXISTS TicketEvent (
    event_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    event_type TEXT NOT NULL
        CHECK (event_type IN (
            'ticket_created',
            'status_changed',
            'priority_changed',
            'assignment_changed',
            'queue_changed',
            'escalated',
            'message_added',
            'sla_breached',
            'ticket_resolved',
            'ticket_closed',
            'policy_cited',
            'anomaly_detected'
        )),
    actor_type TEXT NOT NULL
        CHECK (actor_type IN (
            'employee',
            'assistant',
            'hr_agent',
            'system'
        )),
    actor_employee_id TEXT,
    event_details TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES Ticket(ticket_id),

    FOREIGN KEY (actor_employee_id)
        REFERENCES Employee(employee_id),

    CHECK (
        actor_type IN ('assistant', 'system')
        OR actor_employee_id IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_employee_department
ON Employee(department_id);

CREATE INDEX IF NOT EXISTS idx_policy_version_policy
ON PolicyVersion(policy_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_article_version
ON KnowledgeArticle(policy_version_id);

CREATE INDEX IF NOT EXISTS idx_ticket_requester
ON Ticket(requester_employee_id);

CREATE INDEX IF NOT EXISTS idx_ticket_status
ON Ticket(status);

CREATE INDEX IF NOT EXISTS idx_ticket_category
ON Ticket(category_id);

CREATE INDEX IF NOT EXISTS idx_ticket_created
ON Ticket(created_at);

CREATE INDEX IF NOT EXISTS idx_message_ticket
ON Message(ticket_id);

CREATE INDEX IF NOT EXISTS idx_assignment_ticket
ON Assignment(ticket_id);

CREATE INDEX IF NOT EXISTS idx_ticket_event_ticket
ON TicketEvent(ticket_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_assignment
ON Assignment(ticket_id)
WHERE assignment_status = 'active';

