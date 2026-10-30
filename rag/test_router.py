
from .router import classify_query


test_questions = [
    "What is the annual leave policy?",
    "I want to report sexual harassment at work.",
    "My salary was deducted incorrectly.",
    "I am facing workplace discrimination.",
    "What is the parental leave policy?",
    "My manager is bullying me."
]


for question in test_questions:
    result = classify_query(question)

    print("\nQuestion:", question)
    print("Category:", result["category"])
    print("Route:", result["route"])
    print("Human intervention:", result["requires_human"])
