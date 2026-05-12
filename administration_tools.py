import mysql.connector
import re

def search_administration(query):
    q = query.lower().strip()

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="university_chatbot"
    )

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT position_name, content, page_link
        FROM administration
        WHERE LOWER(position_name) LIKE %s
        LIMIT 1
    """, (f"%{q}%",))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    content = row.get("content") or ""

    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", content)
    phone_match = re.search(
        r"(\+91[-\s]?\d{10}|0522[-\s]?\d{6,10}|1800[-\s]?\d{3}[-\s]?\d{4})",
        content
    )

    return {
        "position_name": row["position_name"],
        "email": email_match.group() if email_match else "Not Available",
        "phone": phone_match.group() if phone_match else "Not Available",
        "page_link": row["page_link"]
    }