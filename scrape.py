from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.get("https://www.bbau.ac.in/Faculty.aspx?pn=1&dsg=Professor&scl=SH3&dept=DP8&")

time.sleep(5)
 
elements = driver.find_elements(By.CLASS_NAME, "faculty-name")

for el in elements:
    print(el.text)

driver.quit()


