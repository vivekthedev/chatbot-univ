import mysql.connector

def get_all_schools():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="university_chatbot"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT school_name FROM school")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def get_all_departments():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="university_chatbot"
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT department_name FROM department")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows