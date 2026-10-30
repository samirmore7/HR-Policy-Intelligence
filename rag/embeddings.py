
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent.parent
CHUNKS_PATH = BASE_DIR / "data" / "policy_chunks.json"
EMBEDDINGS_PATH = BASE_DIR / "data" / "policy_embeddings.npy"

MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_embeddings(chunks):
    model = SentenceTransformer(MODEL_NAME)

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    return embeddings


def main():
    chunks = load_chunks()

    if not chunks:
        print("No policy chunks found.")
        return

    embeddings = generate_embeddings(chunks)

    np.save(EMBEDDINGS_PATH, embeddings)

    print("\nEmbedding generation completed!")
    print("Total chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)
    print("Vector dimensions:", embeddings.shape[1])
    print("Saved to:", EMBEDDINGS_PATH)


if __name__ == "__main__":
    main()
