import pandas as pd
import re
import numpy as np

def extract_number(text):
    text = text.replace(',', '')
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    else:
        return None
    
rentals = pd.read_csv('../web_scrape/australia_wide/combined_rent.csv').drop_duplicates(subset=['address']).drop('Unnamed: 0', axis = 1)
sales = pd.read_csv('../web_scrape/australia_wide/combined_sold.csv').drop_duplicates(subset=['address']).drop('Unnamed: 0', axis = 1)

# modify sales
sales['price'] = sales['price'].apply(extract_number)

# modify rentals
rentals['rent'] = rentals['rent'].apply(extract_number)
rentals = rentals[rentals['rent'] > 200]

rentals = rentals.dropna()
sales = sales.dropna()

merged_df = pd.merge(rentals, sales, how='inner', left_on='address', right_on='address')
merged_df['yield'] = (merged_df['rent'].astype(int) * 52) / merged_df['price'].astype(int)
merged_df.to_csv('merged.csv')


# rentals = rentals[rentals['rent'] < (np.mean(rentals['rent']) + 2* np.std(rentals['rent']))]

# 1bd
rent_1bd = rentals[rentals['bedrooms'] == '1']
sales_1bd = sales[sales['bedrooms'] == '1']
print('1 BD')
print(np.median(rent_1bd['rent']))
print(np.median(sales_1bd['price']))
print(((np.median(rent_1bd['rent'])) * 52)/ np.median(sales_1bd['price']))

# # 2bd
rent_2bd = rentals[rentals['bedrooms'] == '2']
sales_2bd = sales[sales['bedrooms'] == '2']
print('2BD')
print(np.median(rent_2bd['rent']))
print(np.median(sales_2bd['price']))
print((int(np.median(rent_2bd['rent'])) * 52)/ np.median(sales_2bd['price']))

# 3bd
rent_3bd = rentals[rentals['bedrooms'] == '3']
sales_3bd = sales[sales['bedrooms'] == '3']
print('3BD')
print(np.median(rent_3bd['rent']))
print(np.median(sales_3bd['price']))
print((int(np.median(rent_3bd['rent'])) * 52)/ np.median(sales_3bd['price']))

rentals['post_code'] = rentals['address'].apply(lambda x: x.split()[-1])
sales['post_code'] = sales['address'].apply(lambda x: x.split()[-1])

summary_list = []
house_types = ['Apartment / Unit / Flat', 'House', 'Townhouse']
for post_code in rentals['post_code'].unique():
    
    rentals_spec = rentals[rentals['post_code'] == post_code]
    sales_spec = sales[sales['post_code'] == post_code]
    
    for index, row in sales_spec.iterrows():
        if row['type'] not in house_types:
            sales_spec.at[index, 'type'] = row['floor_size']  # Set to value of column2 or any other column

    
    for house_type in house_types:
        for br in range(1,4):
            
            rent_br = rentals_spec[((rentals_spec['bedrooms'] == str(br)) & (rentals_spec['type'] == house_type))]
            sales_br = sales_spec[((sales_spec['bedrooms'] == str(br)) & (sales_spec['type'] == house_type))]
            
            if len(rent_br) > 5 and len(sales_br) > 10:
                data = {
                            'post_code' : post_code,
                            'bedrooms' : br,
                            'type' : house_type,
                            'yield' : (int(np.median(rent_br['rent'])) * 52)/ np.median(sales_br['price']),
                            'median rent': int(np.median(rent_br['rent'])),
                            'median value': int(np.median(sales_br['price'])),
                            'num. sales': len(sales_br),
                            'num_rentals': len(rent_br)
                        }
                summary_list.append(data)
        
summary_df = pd.DataFrame(summary_list).sort_values(by='yield', ascending=False)

summary_df.to_csv('yield_summary_all_aus.csv')
