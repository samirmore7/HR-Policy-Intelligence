
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent.parent

CHUNKS_PATH = BASE_DIR / "data" / "policy_chunks.json"
EMBEDDINGS_PATH = BASE_DIR / "data" / "policy_embeddings.npy"

MODEL_NAME = "all-MiniLM-L6-v2"


class PolicyRetriever:

    def __init__(self):
        with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
            self.chunks = json.load(file)

        self.embeddings = np.load(EMBEDDINGS_PATH)

        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query, top_k=3):
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        scores = np.dot(
            self.embeddings,
            query_embedding.T
        ).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            chunk = self.chunks[index]

            results.append({
                "chunk_id": chunk["chunk_id"],
                "policy_id": chunk["policy_id"],
                "policy_code": chunk["policy_code"],
                "policy_title": chunk["policy_title"],
                "policy_version_id": chunk["policy_version_id"],
                "version_number": chunk["version_number"],
                "effective_start": chunk["effective_start"],
                "effective_end": chunk["effective_end"],
                "category": chunk["category"],
                "content": chunk["content"],
                "similarity_score": round(
                    float(scores[index]), 4
                )
            })

        return results


if __name__ == "__main__":
    retriever = PolicyRetriever()

    query = "What is the company's annual leave policy?"

    results = retriever.search(query, top_k=3)

    print("\nEmployee question:")
    print(query)

    print("\nRetrieved policies:")

    for result in results:
        print("\nPolicy:", result["policy_title"])
        print("Version:", result["policy_version_id"])
        print("Similarity:", result["similarity_score"])
        print("Content:", result["content"])
