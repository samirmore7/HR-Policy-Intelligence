
import sqlite3
from pathlib import Path

schema_path = Path(__file__).with_name("schema.sql")
database_path = Path(__file__).parent.parent / "data" / "hr_policy.db"

connection = sqlite3.connect(database_path)
connection.execute("PRAGMA foreign_keys = ON")

try:
    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    connection.executescript(schema)

    print("Database schema created successfully!")

    tables = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """).fetchall()

    print("\nTables created:")
    for table in tables:
        print("-", table[0])

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if foreign_keys:
        print("\nForeign key issues:", foreign_keys)
    else:
        print("\nForeign key check passed!")

    print("\nDatabase setup completed successfully!")

except sqlite3.Error as error:
    print("\nDatabase error:", error)

finally:
    connection.close()
