import mysql.connector
from rapidfuzz import fuzz

def detect_intent(question):

    q = question.lower().strip()

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="university_chatbot"
    )

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT keywords, response FROM intent")

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    for row in rows:

        keywords = row["keywords"].split(",")

        for key in keywords:

            key = key.strip().lower()

            if fuzz.token_sort_ratio(q, key) > 85:
                return row["response"]

    return None