
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "data" / "hr_policy.db"
OUTPUT_PATH = BASE_DIR / "data" / "policy_chunks.json"


def load_policies():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        policies = connection.execute("""
            SELECT
                d.policy_id,
                d.policy_code,
                d.title,
                d.category_code,
                v.policy_version_id,
                v.version_number,
                v.effective_start,
                v.effective_end,
                v.audience,
                v.status,
                v.policy_content
            FROM PolicyDocument d
            JOIN PolicyVersion v
                ON d.policy_id = v.policy_id
            WHERE v.status = 'effective'
              AND d.lifecycle_state = 'published'
            ORDER BY d.policy_code
        """).fetchall()

        return [dict(policy) for policy in policies]

    finally:
        connection.close()


def split_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def create_chunks(policies):
    all_chunks = []

    for policy in policies:
        text_chunks = split_text(policy["policy_content"])

        for index, content in enumerate(text_chunks):
            all_chunks.append({
                "chunk_id": (
                    f"{policy['policy_version_id']}-"
                    f"CHUNK-{index + 1:03d}"
                ),
                "policy_id": policy["policy_id"],
                "policy_code": policy["policy_code"],
                "policy_title": policy["title"],
                "policy_version_id": policy["policy_version_id"],
                "version_number": policy["version_number"],
                "effective_start": policy["effective_start"],
                "effective_end": policy["effective_end"],
                "audience": policy["audience"],
                "category": policy["category_code"],
                "content": content
            })

    return all_chunks


def save_chunks(chunks):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=4, ensure_ascii=False)


def main():
    policies = load_policies()
    chunks = create_chunks(policies)
    save_chunks(chunks)

    print("Policy ingestion completed!")
    print("Effective policies:", len(policies))
    print("Total chunks:", len(chunks))
    print("Saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
