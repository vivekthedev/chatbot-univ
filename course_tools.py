import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor(dictionary=True)

def search_course(query):

    query = query.lower()

    cursor.execute(
        """
        SELECT *
        FROM course
        WHERE LOWER(course_name) LIKE %s
        """,
        (f"%{query}%",)
    )

    return cursor.fetchall()