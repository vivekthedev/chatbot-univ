import json
import os
import time
import requests
from bs4 import BeautifulSoup

DATA_FILE = "faculty_data.json"
SCRAPED_URLS_FILE = "scraped_urls.json"

schools = [
    'SH1', 'SH18', 'SH17', 'SH13', 'SH4', 'SH5', 'SH22', 'SH6', 'SH3',
    'SH10', 'SH7', 'SH2', 'SH8', 'SH11', 'SH21', 'SH14', 'SH9', 'SH19',
    'SH20', 'SH16'
]

departments = [
    'DP46', 'DP35', 'DP6', 'DP27', 'DP61', 'DP30', 'DP17', 'DP36', 'DP42',
    'DP44', 'DP34', 'DP37', 'DP8', 'DP47', 'DP22', 'DP11', 'DP38', 'DP39',
    'DP49', 'DP25', 'DP10', 'DP50', 'DP51', 'DP45', 'DP20', 'DP1', 'DP48',
    'DP23', 'DP12', 'DP13', 'DP7', 'DP43', 'DP41', 'DP14', 'DP9', 'DP15',
    'DP21', 'DP16', 'DP40', 'DP33', 'DP55', 'DP62', 'DP24', 'DP58', 'DP18',
    'DP2', 'DP54', 'DP53', 'DP4', 'DP31', 'DP32', 'DP56', 'DP59', 'DP3',
    'DP57', 'DP19', 'DP60', 'DP5'
]

def load_json_file(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

faculty_data = load_json_file(DATA_FILE, [])
scraped_urls = load_json_file(SCRAPED_URLS_FILE, [])

scraped_urls_set = set(scraped_urls)

existing_faculty_keys = set()
for f in faculty_data:
    key = (
        f.get("Name", "").lower(),
        f.get("Department", "").lower(),
        f.get("School", "").lower()
    )
    existing_faculty_keys.add(key)

url_list = [
    f"https://www.bbau.ac.in/Faculty.aspx?pn=1&scl={scl}&dept={dept}&"
    for scl in schools
    for dept in departments
]

for url in url_list:

    if url in scraped_urls_set:
        print("Skipping already scraped:", url)
        continue

    print("Scraping:", url)

    try:
        res = requests.get(url, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")

        prof_sections = soup.find_all("div", class_="col-md-6")

        for section in prof_sections:
            panel = section.find("div", class_="panel-body")
            if not panel:
                continue

            profile_data = {}

            name_container = panel.find("div", class_="col-xs-9")
            if name_container:
                name_tag = name_container.find("b")
                if name_tag:
                    profile_data["Name"] = name_tag.text.strip()

                designation_tag = name_container.find("small")
                if designation_tag:
                    profile_data["Designation"] = designation_tag.text.strip()

                links = name_container.find_all("a")
                if len(links) >= 3:
                    profile_data["Department"] = links[1].text.strip()
                    profile_data["School"] = links[2].text.strip()

            bottom_panel = panel.find("div", class_="panelBottom")
            if bottom_panel:
                bottom_p = bottom_panel.find("p")

                if bottom_p:
                    for b_tag in bottom_p.find_all("b"):
                        key = b_tag.text.strip().replace(" :", "").strip()

                        if key == "Contact":
                            continue

                        value = b_tag.next_sibling
                        if value and isinstance(value, str) and value.strip():
                            profile_data[key] = value.strip()

                    phone_span = bottom_p.find("span", class_="fa-phone")
                    if phone_span and phone_span.next_sibling:
                        phone_text = phone_span.next_sibling.strip().strip(":\xa0 ")
                        if phone_text:
                            profile_data["Phone"] = phone_text

                    email_tag = bottom_p.find("a", href=lambda href: href and href.startswith("mailto:"))
                    if email_tag and email_tag.text.strip():
                        profile_data["Email"] = email_tag.text.strip()

            if profile_data.get("Name"):
                faculty_key = (
                    profile_data.get("Name", "").lower(),
                    profile_data.get("Department", "").lower(),
                    profile_data.get("School", "").lower()
                )

                if faculty_key not in existing_faculty_keys:
                    faculty_data.append(profile_data)
                    existing_faculty_keys.add(faculty_key)

        scraped_urls.append(url)
        scraped_urls_set.add(url)

        save_json_file(DATA_FILE, faculty_data)
        save_json_file(SCRAPED_URLS_FILE, scraped_urls)

        time.sleep(1)

    except Exception as e:
        print("Error:", url, e)

print("Done ✅")
print("Total faculty:", len(faculty_data))
print("Total scraped urls:", len(scraped_urls))