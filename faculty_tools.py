import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor(dictionary=True)

def search_faculty(query):
    query = query.lower()

    remove_words = [
        "who is", "tell me about", "show me", "details of",
        "faculty", "faculties", "professor", "sir", "mam",
        "department", "school", "of", "the", "in"
    ]

    for word in remove_words:
        query = query.replace(word, "")

    query = query.strip()

    words = query.split()

    if not words:
        return []

    sql = """
    SELECT * FROM faculty
    WHERE
    """

    conditions = []
    values = []

    for word in words:
        conditions.append("""
        (
            LOWER(name) LIKE %s
            OR LOWER(department) LIKE %s
            OR LOWER(school) LIKE %s
        )
        """)
        values.extend([f"%{word}%", f"%{word}%", f"%{word}%"])

    sql += " AND ".join(conditions)

    cursor.execute(sql, values)
    return cursor.fetchall()