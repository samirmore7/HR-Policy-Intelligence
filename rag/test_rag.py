
from .retriever import PolicyRetriever
from .generator import generate_answer


def main():
    retriever = PolicyRetriever()

    question = "What is the company's annual leave policy?"

    print("\nEmployee question:")
    print(question)

    results = retriever.search(question, top_k=3)

    print("\nRetrieved policies:")

    for result in results:
        print(
            f"- {result['policy_title']} "
            f"({result['policy_version_id']}) "
            f"| Similarity: {result['similarity_score']}"
        )

    print("\nGenerating AI answer...")

    answer = generate_answer(question, results)

    print("\nAI Generated Answer:")
    print(answer)


if __name__ == "__main__":
    main()

