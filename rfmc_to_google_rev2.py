#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
import re

def format_phone_number(number):
    # Remove any non-digit characters from the input string
    digits = re.sub(r'\D', '', number)
    
    # If the resulting string has 11 digits and starts with 1, remove the 1
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]
    
    # Check if the resulting string has 10 digits
    if len(digits) == 10:
        # If it has 10 digits, format it as (XXX) XXX-XXXX
        return '({}) {}-{}'.format(digits[:3], digits[3:6], digits[6:])
    else:
        # If it doesn't have 10 digits, return the original string
        return number

# Read the input xlsx file
input_folder = 'inputriders'
output_folder = 'outputriders'
input_file = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')][0]

# Read the input sheet
df = pd.read_excel(os.path.join(input_folder, input_file), engine='openpyxl', sheet_name=0)

regular_df = df.copy()


# Process the regular DataFrame
regular_df['Name'] = regular_df['Attendee First Name'] + ' ' + regular_df['Attendee Last Name']
regular_df['Given Name'] = regular_df['Attendee First Name']
regular_df['Family Name'] = regular_df['Attendee Last Name']
regular_df = regular_df.rename(columns={
        'Attendee First Name': 'Given Name',
        'Attendee Last Name': 'Family Name',
        'Email': 'E-mail 1 - Value',
        'Cell Phone': 'Phone 1 - Value',
        })
regular_df['Phone 1 - Value'] = regular_df['Phone 1 - Value'].astype(str)
regular_df['Phone 1 - Value'] = regular_df['Phone 1 - Value'].apply(format_phone_number)  # Format phone numbers

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
    if header not in regular_df.columns:
        regular_df[header] = np.nan


# Save the processed DataFrames to output files
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.splitext(input_file)[0]
regular_df.to_csv(os.path.join(output_folder, f'{output_file}_regular.csv'), columns=output_headers, index=False)

