from langchain_community.llms import Ollama
from faculty_tools import faculty_by_name, faculty_by_department
import mysql.connector

llm = Ollama(model="phi3:mini")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor()

while True:
    question = input("\nAsk Question: ")
     
    # Administration Search

    cursor.execute("""
    SELECT position_name, content
    FROM administration
    """)

    admin_rows = cursor.fetchall()

    found_admin = False

    for row in admin_rows:
        position = row[0].lower()
        content = row[1]

        if position in question.lower():
            print("\nAnswer:\n")
            print(content[:3000])
            found_admin = True
            break

    if found_admin:
        continue

    if question.lower() == "exit":
        break

    # Faculty by name
    if "faculty" in question.lower() or "professor" in question.lower():

        if "computer" in question.lower():
            result = faculty_by_department("Computer")
            print("\nAnswer:")
            for f in result:
                print("\nName:", f["name"])
                print("Designation:", f["designation"])
                print("Department:", f["department"])
                print("School:", f["school"])
                print("Specialization:", f["specialization"])
                print("Qualification:", f["qualification"])
                print("Teaching Experience:", f["teaching_experience"])
                print("Research Experience:", f["research_experience"])
                print("Phone:", f["phone"])
                print("Email:", f["email"])

        else:
            words = question.split()
            name = words[-1]

            result = faculty_by_name(name)

            print("\nAnswer:")
            for f in result:
                print("\nName:", f["name"])
                print("Designation:", f["designation"])
                print("Department:", f["department"])
                print("School:", f["school"])
                print("Specialization:", f["specialization"])
                print("Qualification:", f["qualification"])
                print("Teaching Experience:", f["teaching_experience"])
                print("Research Experience:", f["research_experience"])
                print("Phone:", f["phone"])
                print("Email:", f["email"])

    else:
        response = llm.invoke(question)

        print("\nAnswer:")
        print(response)