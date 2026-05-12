import json
import re
import requests
import mysql.connector
from bs4 import BeautifulSoup

URLS = [
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=Ph.D",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=M.Phil",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=Bsc-Msc",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=BBA-LLB",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=M.Sc",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=M.Tech",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=M.A",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=LLM",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=M.Pharm",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=BTech",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=BBA",
    "https://www.bbau.ac.in/Courses.aspx?pn=1&txt=BSc",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

VALID_STARTS = (
    "B.Tech", "B.Sc", "BBA", "M.Sc", "M.Tech", "M.A", "M.Pharm",
    "MCA", "MBA", "LLM", "Ph.D", "M.Phil"
)

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def get_level(name):
    n = name.lower()
    if "ph.d" in n:
        return "Doctoral"
    if "m.phil" in n:
        return "M.Phil"
    if n.startswith(("m.", "mba", "mca", "llm")):
        return "PG"
    if n.startswith(("b.", "bba")):
        return "UG"
    return ""

def is_valid_programme_name(name):
    if not name:
        return False
    bad_words = ["BBAU ERP", "Sitemap", "Samarth", "Login", "Tender", "Result"]
    if any(bad.lower() in name.lower() for bad in bad_words):
        return False
    return name.startswith(VALID_STARTS)

all_programmes = []
seen = set()

for url in URLS:
    print("Scraping:", url)

    res = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(res.text, "html.parser")

    text = clean(soup.get_text(" ", strip=True))

    pattern = r"(B\.Tech\.?.*?|B\.Sc\.?.*?|BBA-LLB.*?|BBA.*?|M\.Sc\.?.*?|M\.Tech\.?.*?|M\.A\.?.*?|M\.Pharm.*?|LLM.*?|Ph\.D\.?.*?|M\.Phil.*?)\s+(Department of .*?)\s+Duration\s+(.*?)\s+Intake\s+(.*?)\s+Fees\s+\(Semester\)\s+(.*?)\s+(?=(?:B\.Tech|B\.Sc|BBA|M\.Sc|M\.Tech|M\.A|M\.Pharm|LLM|Ph\.D|M\.Phil|Quick Links|Useful Links|$))"

    matches = re.findall(pattern, text, re.IGNORECASE)

    for m in matches:
        programme_name = clean(m[0])
        department_name = clean(m[1])
        duration = clean(m[2])
        intake = clean(m[3])
        fees = clean(m[4])

        if not is_valid_programme_name(programme_name):
            continue

        key = (programme_name.lower(), department_name.lower())

        if key in seen:
            continue

        seen.add(key)

        all_programmes.append({
            "programme_name": programme_name,
            "level": get_level(programme_name),
            "duration": duration,
            "eligibility": "Available on university website",
            "department_name": department_name,
            "intake": intake,
            "fees": fees
        })

print("Total programmes scraped:", len(all_programmes))

with open("programme_data.json", "w", encoding="utf-8") as f:
    json.dump(all_programmes, f, indent=4, ensure_ascii=False)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)

cursor = conn.cursor()

cursor.execute("DELETE FROM programme")

for p in all_programmes:
    cursor.execute(
        """
        INSERT INTO programme
        (programme_name, level, duration, eligibility, department_name, intake, fees)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            p["programme_name"],
            p["level"],
            p["duration"],
            p["eligibility"],
            p["department_name"],
            p["intake"],
            p["fees"]
        )
    )

conn.commit()
cursor.close()
conn.close()

print("Programme data saved in JSON ✅")
print("Programme data inserted into DB ✅")