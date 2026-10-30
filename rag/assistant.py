
from .router import classify_query
from .retriever import PolicyRetriever
from .generator import generate_answer
from .escalation import create_escalation


class HRPolicyAssistant:

    def __init__(self):
        self.retriever = PolicyRetriever()

    def ask(self, question, ticket_id=None):
        routing_result = classify_query(question)

        if routing_result["requires_human"]:

            escalation = None

            if ticket_id:
                escalation = create_escalation(
                    ticket_id=ticket_id,
                    category=routing_result["category"],
                    reason=routing_result["reason"]
                )

            return {
                "route": routing_result["route"],
                "category": routing_result["category"],
                "requires_human": True,
                "answer": (
                    "Your request requires human HR assistance. "
                    "The matter has been identified for HR escalation."
                    if ticket_id
                    else "Your request requires human HR assistance."
                ),
                "sources": [],
                "escalation": escalation
            }

        retrieved_chunks = self.retriever.search(
            question,
            top_k=3
        )

        answer = generate_answer(
            question,
            retrieved_chunks
        )

        sources = []

        for chunk in retrieved_chunks:
            sources.append({
                "policy_title": chunk["policy_title"],
                "policy_version": chunk["policy_version_id"],
                "similarity_score": chunk["similarity_score"]
            })

        return {
            "route": routing_result["route"],
            "category": routing_result["category"],
            "requires_human": False,
            "answer": answer,
            "sources": sources,
            "escalation": None
        }
