
from .assistant import HRPolicyAssistant


def main():
    assistant = HRPolicyAssistant()

    questions = [
        "What is the company's annual leave policy?",
        "I want to report sexual harassment at work.",
        "My salary was deducted incorrectly.",
        "What is the parental leave policy?"
    ]

    for question in questions:
        print("\n" + "=" * 60)
        print("EMPLOYEE QUESTION:")
        print(question)

        result = assistant.ask(question)

        print("\nROUTE:", result["route"])
        print("CATEGORY:", result["category"])
        print("HUMAN INTERVENTION:", result["requires_human"])

        print("\nANSWER:")
        print(result["answer"])

        if result["sources"]:
            print("\nPOLICY SOURCES:")

            for source in result["sources"]:
                print(
                    f"- {source['policy_title']} "
                    f"({source['policy_version']}) "
                    f"| Score: {source['similarity_score']}"
                )


if __name__ == "__main__":
    main()
