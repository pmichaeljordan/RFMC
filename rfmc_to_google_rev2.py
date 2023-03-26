#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import re

# Read the input xlsx file
input_folder = 'inputriders'
output_folder = 'outputriders'
input_file = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')][0]

# Read the input sheet
df = pd.read_excel(os.path.join(input_folder, input_file), engine='openpyxl', sheet_name=0)

riders_df = df.copy()


# Process the regular DataFrame
riders_df['Name'] = riders_df['Attendee First Name'] + ' ' + riders_df['Attendee Last Name']
riders_df['Given Name'] = riders_df['Attendee First Name']
riders_df['Family Name'] = riders_df['Attendee Last Name']
riders_df = riders_df.rename(columns={
        # 'Attendee First Name': 'Given Name',
        # 'Attendee Last Name': 'Family Name',
        'Billing Email Address': 'E-mail 1 - Value',
        'Cell Phone': 'Phone 1 - Value',
        })


# Define the output headers
output_headers = [
    'Name', 'Given Name', 'Additional Name', 'Family Name', 'Yomi Name',
    'Given Name Yomi', 'Additional Name Yomi', 'Family Name Yomi', 'Name Prefix',
    'Name Suffix', 'Initials', 'Nickname', 'Short Name', 'Maiden Name', 'Birthday',
    'Gender', 'Location', 'Billing Information', 'Directory Server', 'Mileage',
    'Occupation', 'Hobby', 'Sensitivity', 'Priority', 'Subject', 'Notes', 'Language',
    'Photo', 'Group Membership', 'E-mail 1 - Type', 'E-mail 1 - Value', 'Phone 1 - Type',
    'Phone 1 - Value', 'Phone 2 - Type', 'Phone 2 - Value', 'date', 'Emergency Contact First name'
]
for header in output_headers:
    if header not in riders_df.columns:
        riders_df[header] = np.nan


# Save the processed DataFrames to output files
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.splitext(input_file)[0]
riders_df.to_csv(os.path.join(output_folder, f'{output_file}_riders.csv'), columns=output_headers, index=False)

