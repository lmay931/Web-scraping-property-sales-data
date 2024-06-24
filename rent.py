from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

def scrape_text(parent_element, props_list):

    child_elements = parent_element.find_elements(By.TAG_NAME, 'li')
    for element in child_elements:
        
        listing = element.text.split('\n')
        
        if len(listing) > 9:  
            try: 
                while listing[0][0] != '$': # remove agents name
                    listing.pop(0)
            except:
                continue
            if len(listing) < 9:
                continue
            if not listing[7].isnumeric(): listing[7] = 0 # setting 0 carparks to correct format
            if listing[-1][0:10] == 'INSPECTION':
                listing.pop(-1)
            
            listing_data = {
                    'address' : f'{listing[1]} {listing[2]}',
                    'rent' : listing[0],
                    'bedrooms' : listing[3],
                    'bathrooms': listing[5],
                    'carparks': listing[7],
                    'type': listing[-1],
                    'floor_size': listing[-2]
                }
            
            if listing[-1] == 'Parking':
                continue
            props_list.append(listing_data)
            
    return props_list

combined_properties_list = []

for post_code in range(2000, 4000):
    url = f"https://www.domain.com.au/rent/?ptype=apartment-unit-flat,duplex,free-standing,semi-detached,terrace,town-house,villa&excludedeposittaken=1&ssubs=0&postcode={post_code}"
    driver.get(url)
    print(post_code)
    first_page = True
    
    while True:
        
        time.sleep(10)
        if driver.find_element(By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[1]/h1/strong').text == '0 Properties':
            break

        # Find the parent element
        parent_element = driver.find_element(By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[2]/ul')
    
        # Scrape text
        combined_properties_list = scrape_text(parent_element, combined_properties_list)
    
        # Wait for 10 seconds
        time.sleep(10)
    
        if first_page:
            try:
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[3]/div[1]/div/a')))
                element.click()
                first_page = False
            except:
                break
        else:
            try:
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[3]/div[1]/div/a[2]')))
                element.click()
            except:
                break

        time.sleep(10)        
        listing_df = pd.DataFrame(combined_properties_list)
        listing_df.to_csv(f'../web_scrape/australia_wide/rent/rentals_{post_code}.csv')
   

# quit driver
driver.quit()