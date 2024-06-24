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
                while listing[1][0] != '$': # remove agents name
                    listing.pop(1)
            except:
                continue
            
            if len(listing) < 9:
                continue
            
            if not listing[8].isnumeric(): listing[8] = 0 # setting 0 carparks to correct format
            
            listing_data = {
                    'sale_date': listing[0],
                    'address' : f'{listing[2]} {listing[3]}',
                    'price' : listing[1],
                    'bedrooms' : listing[4],
                    'bathrooms': listing[6],
                    'carparks': listing[8],
                    'floor_size': listing[-2],
                    'type': listing[-1]
                }
            
            if listing[-1] == 'Parking':
                continue
            props_list.append(listing_data)
            
    return props_list

    
combined_properties_list = []
year = 2024

for post_code in range(2000, 2001):
    url = f"https://www.domain.com.au/sold-listings/?ptype=apartment-unit-flat,duplex,free-standing,semi-detached,terrace,town-house,villa&postcode={post_code}&excludepricewithheld=1"
    driver.get(url)
    
    time.sleep(10)
    first_page = True
    
    if driver.find_element(By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[1]/h1/strong').text == '0 Properties':
        continue
    
    print(post_code)
    
    while year > 2022:
        # Find the parent element
        try:
            parent_element = driver.find_element(By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[2]/ul')
        except:
            break
        # Scrape text
        combined_properties_list = scrape_text(parent_element, combined_properties_list)
        year = combined_properties_list[-1]['sale_date'].split(' ')[-1]
        if year == 'available.':
            break
        else: 
            year = int(year)
        
        if int(driver.find_element(By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[1]/h1/strong').text.split()[0]) < 30:
            break
        
        if first_page:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[3]/div[1]/div/a')))
            element.click()
            first_page = False
        else:
            try:
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[3]/div[1]/div/a[2]')))
                element.click()
            except:
                try:
                    driver.refresh()
                    time.sleep(10)
                    wait = WebDriverWait(driver, 10)
                    element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="skip-link-content"]/div[1]/div[3]/div[1]/div/a[2]')))
                    element.click()
                except:
                    break
        time.sleep(10)
        
        listing_df = pd.DataFrame(combined_properties_list)
        listing_df.to_csv(f'../web_scrape/australia_wide/sold/sold_{post_code}.csv')
    year = 2024
# quit driver
driver.quit()