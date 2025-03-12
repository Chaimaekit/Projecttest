import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017")
db = client["EGX"]
collection = db["indices"]

indices_names = {"EGX30", "EGX70EWI", "EGX100EWI", "SHARIAH", "EGX30CAPPED", "TAMAYUZ", "EGX30ETF"}
all_elements = []

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--enable-javascript')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=chrome_options)

for idx, indice in enumerate(indices_names):
    sub_url = f"https://www.tradingview.com/symbols/EGX-{indice}/"
    driver.get(sub_url)
    time.sleep(5)  # Allow initial content to load

    try:
        # Wait for the first class to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'quotes-kSnhnsc2'))
        )

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'wrapper-GgmpMpKr'))
        )
        
        # Scroll and wait for the second element with retries
        max_attempts = 5
        attempts = 0
        ytd_elements = []  # Initialize ytd_elements variable outside of the loop
        while attempts < max_attempts:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            try:
                ytd_elements = driver.find_elements(By.CLASS_NAME, 'change-tEo1hPMj')
            except Exception as e:
                print(f"Error while finding ytd_elements: {e}")

            if len(ytd_elements) > 0:
                break
            
            # If not found, scroll up and down again
            driver.execute_script("window.scrollBy(0, -300);")
            time.sleep(1)
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(2)
            
            attempts += 1
        
        # Check one last time after scrolling attempts
        if not ytd_elements:
            print(f"Warning: 'change-tEo1hPMj' not found for {indice}")
            ytd = 'N/A'  # Default value if not found
        else:
            ytd = ytd_elements[4].get_attribute('textContent') if len(ytd_elements) > 4 else 'N/A'
        
        # Get all elements with the specified class
        top_elems = driver.find_elements(By.CLASS_NAME, 'quotes-kSnhnsc2')

        # Process the data
        for elems in top_elems:
            spans = elems.find_elements(By.TAG_NAME, 'span')

            # Check if the expected indices exist to avoid IndexError
            if len(spans) > 5:
                element_data = {
                    'name': spans[0].get_attribute('textContent'),
                    'state': spans[1].get_attribute('textContent'),
                    'value': spans[3].get_attribute('textContent') + spans[4].get_attribute('textContent'),
                    'change': spans[8].get_attribute('textContent'),
                    'ytd': ytd  # Use the ytd variable here
                }
                all_elements.append(element_data)

        # Other elements like volume, open, high, low can be added with similar checks
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="js-category-content"]/div[2]/div/section/div[3]/div[2]/div/div[1]/div[2]/div[1]/div'))
        )

        # Get the first element with the specific class
        volume = driver.find_element(By.XPATH, '//*[@id="js-category-content"]/div[2]/div/section/div[3]/div[2]/div/div[1]/div[2]/div[1]/div')
        element_data['volume'] = volume.text

        # Wait for the second element with the same class to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="js-category-content"]/div[2]/div/section/div[3]/div[2]/div/div[2]/div[2]/div[1]/div'))
        )

        # Get the second element
        open = driver.find_element(By.XPATH, '//*[@id="js-category-content"]/div[2]/div/section/div[3]/div[2]/div/div[2]/div[2]/div[1]/div')
        element_data['open'] = open.text

        # Wait for the third element with class 'noBreak-eVYPLch1' to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "noBreak-eVYPLch1")]//span'))
        )

        # Get the third element's span content
        high = driver.find_element(By.XPATH, '//*[contains(@class, "noBreak-eVYPLch1")]//span')
        element_data['high'] = high.text

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "block-eVYPLch1")]//span'))
        )

        # Get the third element's span content
        low = driver.find_element(By.XPATH, '//*[contains(@class, "block-eVYPLch1")]//span')
        element_data['low'] = low.text

        all_elements.append(element_data)

    except TimeoutException:
        print(f"TimeoutException: Element not found for {indice}")
        continue

# Insert all elements into MongoDB as per your previous logic
if all_elements:
    for elems in all_elements:
        existing_doc = collection.find_one({'name': elems['name']})
        if not existing_doc:
            collection.insert_one(elems)
        else:
            print(f"Document with name {elems['name']} already exists.")
    print(f"Inserted {len(all_elements)} elements into MongoDB.")

driver.quit()
