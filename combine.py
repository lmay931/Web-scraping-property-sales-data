import pandas as pd
import os


# Directory containing CSV files
folder_path = '/Users/lawrence/Library/CloudStorage/GoogleDrive-lawrencemrmay@gmail.com/My Drive/Biz/real estate/web_scrape/australia_wide/'

# Loop through each file in the folder
for sub_folder in ['rent', 'sold']:
    print(sub_folder)
    dfs = []
    for filename in os.listdir(folder_path+sub_folder):
        print(filename)
        if filename.endswith('.csv'):
            # Read the CSV file into a DataFrame
            df = pd.read_csv(os.path.join(folder_path+sub_folder, filename)).drop('Unnamed: 0', axis = 1)
            # Append the DataFrame to the list
            dfs.append(df)
            

    # Concatenate all DataFrames into one
    combined_df = pd.concat(dfs, ignore_index=True)

    # Remove duplicates based on the 'address' column
    combined_df.drop_duplicates(subset='address', inplace=True)
    
    # Reset index
    combined_df.reset_index(drop=True, inplace=True)
    combined_df.to_csv(f'../web_scrape/australia_wide/combined_{sub_folder}.csv')