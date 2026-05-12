import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor(dictionary=True)

def search_programme(query):
    query = query.lower().strip()

    programme_keywords = {
        "btech": "b.tech",
        "b.tech": "b.tech",
        "b tech": "b.tech",
        "mtech": "m.tech",
        "m.tech": "m.tech",
        "m tech": "m.tech",
        "msc": "m.sc",
        "m.sc": "m.sc",
        "m sc": "m.sc",
        "bsc": "b.sc",
        "b.sc": "b.sc",
        "b sc": "b.sc",
        "ma": "m.a",
        "m.a": "m.a",
        "m a": "m.a",
        "phd": "ph.d",
        "ph.d": "ph.d",
        "mphil": "m.phil",
        "m.phil": "m.phil",
        "llm": "llm",
        "m.pharm": "m.pharm",
        "mpharm": "m.pharm",
        "bba llb": "bba-llb",
        "bba-llb": "bba-llb",
        "bba": "bba"
    }

    for key, value in programme_keywords.items():
        if key in query:
            cursor.execute(
                "SELECT * FROM programme WHERE LOWER(programme_name) LIKE %s",
                (f"%{value}%",)
            )
            return cursor.fetchall()

    cursor.execute(
        """
        SELECT * FROM programme
        WHERE LOWER(programme_name) LIKE %s
        OR LOWER(department_name) LIKE %s
        OR LOWER(level) LIKE %s
        """,
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )

    return cursor.fetchall()