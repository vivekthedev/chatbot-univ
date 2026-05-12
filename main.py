import requests
from bs4 import BeautifulSoup
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="university_chatbot"
)
cursor = conn.cursor()

links = [
    "https://www.bbau.ac.in/ComputerCentre.aspx",
    "https://www.bbau.ac.in/ComputerCentreNKN.aspx",
    "https://www.bbau.ac.in/CPCAbout.aspx",
    "https://www.bbau.ac.in/IGBAbout.aspx",
    "https://www.bbau.ac.in/RCA.aspx",
    "https://www.bbau.ac.in/RCP.aspx",
    "https://www.bbau.ac.in/DACE.aspx",
    "https://www.bbau.ac.in/Bank.aspx#ATM",
    "https://www.bbau.ac.in/Bank.aspx",
    "https://www.bbau.ac.in/PostOffice.aspx",
    "https://www.bbau.ac.in/CBFWAbout.aspx"
]

for link in links:
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.title.get_text(strip=True)

    content = soup.find("div", class_="col-md-9")
    if content:
        description = content.get_text(" ", strip=True)
    else:
        paragraphs = soup.find_all("p")
        description = " ".join([p.get_text(" ", strip=True) for p in paragraphs])

    if not description:
        description = "Information available on university website"

    cursor.execute(
        "INSERT INTO facility(name, description) VALUES (%s, %s)",
        (title, description)
    )

conn.commit()
print("Facility data inserted successfully ✅")

conn.close()