import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def search_codes(terms, limit=10):
    sql = """
        SELECT code, description,
               MATCH(description) AGAINST(%s IN NATURAL LANGUAGE MODE) AS score
        FROM icd10_codes
        WHERE MATCH(description) AGAINST(%s IN NATURAL LANGUAGE MODE)
        ORDER BY score DESC
        LIMIT %s
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (terms, terms, limit))
        return cursor.fetchall()
    finally:
        conn.close()


if __name__ == "__main__":
    for row in search_codes("type 2 diabetes mellitus"):
        print(row["code"], "-", row["description"])