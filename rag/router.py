
SENSITIVE_KEYWORDS = {
    "harassment": [
        "harassment",
        "sexual harassment",
        "inappropriate behavior",
        "unwanted advances"
    ],
    "discrimination": [
        "discrimination",
        "discriminated",
        "unequal treatment",
        "treated unfairly because"
    ],
    "misconduct": [
        "misconduct",
        "workplace bullying",
        "bullying",
        "my manager is bullying me",
        "threatened by",
        "retaliation",
        "abusive manager"
    ],
    "medical_emergency": [
        "medical emergency",
        "serious injury",
        "hospitalized",
        "emergency treatment"
    ],
    "salary_dispute": [
        "salary dispute",
        "unpaid salary",
        "wrong salary",
        "salary deduction",
        "salary was deducted",
        "deducted incorrectly",
        "incorrect salary",
        "wrong deduction",
        "missing salary"
    ]
}


def classify_query(question):
    question = question.lower()

    for category, keywords in SENSITIVE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question:
                return {
                    "category": category,
                    "route": "HR_ESCALATION",
                    "requires_human": True,
                    "reason": f"Sensitive query detected: {category}"
                }

    return {
        "category": "GENERAL",
        "route": "RAG_ASSISTANT",
        "requires_human": False,
        "reason": "Routine HR policy query"
    }
