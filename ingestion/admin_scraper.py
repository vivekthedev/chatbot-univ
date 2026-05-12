import re
import requests
import mysql.connector
from bs4 import BeautifulSoup

URLS = {
    "Board Of Management": "https://www.bbau.ac.in/BoardOfManagement.aspx",
    "Academic Council": "https://www.bbau.ac.in/AcademicCouncil.aspx",
    "Planning Board": "https://www.bbau.ac.in/PlanningBoard.aspx",
    "Finance Committee": "https://www.bbau.ac.in/FinanceCommitteeMembers.aspx",
    "Visitor": "https://www.bbau.ac.in/Visitor.aspx",
    "Chancellor": "https://www.bbau.ac.in/Chancellor.aspx",
    "Vice Chancellor": "https://www.bbau.ac.in/ViceChancellor.aspx",
    "Ombudsman": "https://www.bbau.ac.in/Ombudsman.aspx",
    "Registrar": "https://www.bbau.ac.in/Registrar.aspx",
    "Finance Officer": "https://www.bbau.ac.in/Finance.aspx",
    "Controller Of Examination": "https://www.bbau.ac.in/Examination.aspx",
    "Proctor": "https://www.bbau.ac.in/Proctor.aspx",
    "Dean Student Welfare": "https://www.bbau.ac.in/DeanStudentWelfare.aspx",
    "Research & Development": "https://www.bbau.ac.in/ResearchDevelopment.aspx",
    "IQAC": "https://www.bbau.ac.in/IQAC.aspx",
    "Hindi Cell": "https://www.bbau.ac.in/HindiCell.aspx",
    "Librarian": "https://www.bbau.ac.in/Librarian.aspx",
    "Dean Academic Affairs": "https://www.bbau.ac.in/DeanAcademic.aspx",
    "Alumni": "https://www.bbau.ac.in/Alumni.aspx",
    "Chief Vigilance Officer": "https://www.bbau.ac.in/CVO.aspx",
    "Deans Of Schools": "https://www.bbau.ac.in/DeansofSchools.aspx",
    "Heads Of Department": "https://www.bbau.ac.in/HeadsofDepartment.aspx"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def get_main_content(soup, category):
    lines = [clean(x) for x in soup.get_text("\n").split("\n") if clean(x)]

    start = 0
    for i, line in enumerate(lines):
        if line.lower() == category.lower():
            start = i
            break

    selected = []
    for line in lines[start:]:
        if line.lower() in ["quick links", "important links", "contact us"]:
            break
        selected.append(line)

    return "\n".join(selected)

def find_email(content):
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", content)
    return match.group() if match else "Not Available"

def find_phone(content):
    match = re.search(r"(\+91[-\s]?\d{8,12}|0522[-\s]?\d{6,10}|1800[-\s]?\d{3}[-\s]?\d{4})", content)
    return match.group() if match else "Not Available"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor()
cursor.execute("DELETE FROM administration")

for category, url in URLS.items():
    print("Scraping:", category)

    response = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    content = get_main_content(soup, category)
    email = find_email(content)
    phone = find_phone(content)

    cursor.execute(
        """
        INSERT INTO administration
        (position_name, person_name, office_phone, email, page_link, content)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            category,
            "See content",
            phone,
            email,
            url,
            content
        )
    )

conn.commit()
cursor.close()
conn.close()

print("Administration exact page content inserted successfully ✅")