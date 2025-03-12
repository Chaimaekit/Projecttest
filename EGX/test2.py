from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient


def main_three():

 myclient = MongoClient("mongodb://localhost:27017")
 mydb = myclient["APSB"]
 collection = mydb["EGX"]



 chrome_options = webdriver.ChromeOptions()
 chrome_options.add_argument('--disable-blink-features=AutomationControlled')
 chrome_options.add_argument('--enable-javascript')

 chrome_options.add_argument('--no-sandbox')
 chrome_options.add_argument('--disable-dev-shm-usage')
 chrome_options.add_argument('--disable-gpu')
 chrome_options.add_argument('--disable-software-rasterizer')
 #chrome_options.add_argument('--proxy-server=23.247.136.245:80')

 chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
 driver = webdriver.Chrome(options=chrome_options)




 driver.get('https://www.egx.com.eg/en/Indices.aspx')
 time.sleep(50)

 def getting_indices(indice_id):

  while True:
    try:
        wait = WebDriverWait(driver, 60)
        element=wait.until(EC.presence_of_element_located((By.ID, indice_id)))
        time.sleep(20)
        element.click()
        print("Page has loaded successfully.")
        break
    except Exception as e:
        print(f"Page did not load properly, retrying... Error: {e}")
        driver.refresh() 
        time.sleep(5) 



 def getting_details():
  html_content = driver.page_source
  soup = BeautifulSoup(html_content, 'html.parser')

  date = soup.find(id="ctl00_C_M_lbldateIndex")
  value = soup.find(id="ctl00_C_M_lblvalueIndex")
  open = soup.find(id="ctl00_C_M_lblOpen")
  volume = soup.find(id="ctl00_C_M_GridView1_ctl02_lblVolume")
  print(f"date: {date.text}  value: {value.text}  open:{open.text}  volume: {volume.text}")
  obj={
    'date': date.text,
    'value': value.text,
    'open': open.text,
    'volume': volume.text
 }
  return obj


 indices_list=['ctl00_C_M_lnkSECTORS','ctl00_C_M_lnkTAMAYUZ']
 for i in range(len(indices_list)):
    getting_indices(indices_list[i])
    obj=getting_details()
    collection.insert_one(obj)
    time.sleep(20)
    
 driver.quit() 

