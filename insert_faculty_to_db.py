import json
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor()

with open("faculty_data.json", "r", encoding="utf-8") as f:
    faculty_data = json.load(f)

for faculty in faculty_data:

    name = faculty.get("Name", "NA")
    designation = faculty.get("Designation", "NA")
    department = faculty.get("Department", "NA")
    school = faculty.get("School", "NA")
    specialization = faculty.get("Specialization", "NA")
    qualification = faculty.get("Qualification", "NA")
    teaching_experience = faculty.get("Teaching Experience", "NA")
    research_experience = faculty.get("Research Experience", "NA")
    phone = faculty.get("Phone", "NA")
    email = faculty.get("Email", "NA")

    sql = """
    INSERT INTO faculty
    (name, designation, department, school,
    specialization, qualification,
    teaching_experience, research_experience,
    phone, email)

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        name,
        designation,
        department,
        school,
        specialization,
        qualification,
        teaching_experience,
        research_experience,
        phone,
        email
    )

    cursor.execute(sql, values)

conn.commit()

print("Faculty data inserted into DB ✅")

conn.close()