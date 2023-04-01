#!/usr/bin/env python3
import os
import glob
import pandas as pd
import datetime
import numpy as np
from excel_writer import ExcelWriter, DataProcessor

# Reformats the sheet sent from NCMEC into something more readable.

def get_formatted_date():
    today = datetime.date.today()
    return today.strftime('%m_%d_%y')


def get_latest_file(path):
    list_of_files = glob.glob(path + '*.xlsx')
    return max(list_of_files, key=os.path.getctime)


def process_dataframes(latest_file):
    df = pd.read_excel(latest_file)

    riders_start = 0
    riders_end = df[df.iloc[:, 0] == 'END'].index[0]

    riders_df = df.iloc[riders_start:riders_end]
# Convert "Cell Phone" column to string type, then apply formatting
    riders_df.loc[:, 'Cell Phone'] = riders_df['Cell Phone'].astype(str)
    riders_df.loc[:, 'Cell Phone'] = riders_df['Cell Phone'].apply(DataProcessor.format_phone_number)
    # riders_df.loc['Home Phone'] = riders_df['Home Phone'].replace({np.nan: None})
    riders_df.loc[:, 'Home Phone'] = riders_df['Home Phone'].astype(str)
    riders_df.loc[:, 'Home Phone'] = riders_df['Home Phone'].apply(DataProcessor.format_phone_number)
    riders_df.loc[:, 'Home Phone'] = riders_df['Home Phone'].replace({np.nan: None})
    riders_df.loc[:, 'Home Phone'] = riders_df['Home Phone'].replace({'nan': None})

    riders_df = riders_df.iloc[:, :riders_df.columns.get_loc('Billing Email Address')+1]
    riders_df = df.sort_values(by='Attendee Last Name', ascending=True)


# # Rename the headers for the addon_riders_df
#     addon_riders_start = riders_end + 1
#     addon_riders_end = df[df.iloc[:, 0] == 'VOLUNTEERS'].index[0]
#     addon_riders_df = df.iloc[addon_riders_start:addon_riders_end]
#     addon_riders_df = addon_riders_df.rename(columns={
#         'Created Date': 'Attendee First Name',
#         'Attendee First Name': 'Attendee Last Name',
#         'Attendee Last Name': 'Add-on rider',
#         'Ticket Name': '2023 Add-on Cities',
#         'Are you a New or Returning Participant?': 'Email Address'
#     })
#     #addon_riders_df = addon_riders_df.drop(columns=['Birth Date'])
#     addon_riders_df = df.sort_values(by='Attendee Last Name', ascending=True)

#     volunteers_start = addon_riders_end + 1
#     volunteers_df = df.iloc[volunteers_start:].dropna(axis='columns', how='all')
#     # volunteers_df = volunteers_df.rename(columns={
#     #     'Are you a New or Returning Participant?': 'Billing Email Address',
#     #     'Birth Date': 'New / Returning',
#     #     'Cell Phone': 'Birth Date',
#     #     'City': 'Cell Phone',
#     #     'Do you have any allergies or health concerns?': 'City',
#     #     "If you were recruited by a past rider please provide the rider's first and last name.": 'Emergency Contact First Name',
#     #     "If you were recruited by a past rider please provide the rider's first and last name..1": 'Sex',
#     #     "JERSEY Size* New Riders ONLY": 'Secondary Phone',
#     #     'Emergency Contact Phone': 'Emergency Contact Phone'
#     # })
# # # Drop any columns that don't have any values in the volunteers_df
# # volunteers_df = df.iloc[volunteers_start:].dropna(axis='columns', how='all')

# # Drop the columns after Emergency Contact Phone in the volunteers_df
#     # volunteers_df = volunteers_df.iloc[:, :volunteers_df.columns.get_loc('Secondary Phone')+1]
#     volunteers_df.loc[:, 'Cell Phone'] = volunteers_df['Cell Phone'].astype(str)
#     volunteers_df.loc[:, 'Cell Phone'] = volunteers_df['Cell Phone'].apply(DataProcessor.format_phone_number)
#     volunteers_df.loc[:, 'Cell Phone'] = volunteers_df['Cell Phone'].replace({np.nan: None})
#     volunteers_df.loc[:, 'Cell Phone'] = volunteers_df['Cell Phone'].replace({'nan': None})
#     # volunteers_df.loc[:, 'Secondary Phone'] = volunteers_df['Secondary Phone'].astype(str)
#     # volunteers_df.loc[:, 'Secondary Phone'] = volunteers_df['Secondary Phone'].apply(DataProcessor.format_phone_number)
#     # volunteers_df.loc[:, 'Secondary Phone'] = volunteers_df['Secondary Phone'].replace({np.nan: None})
#     # volunteers_df.loc[:, 'Secondary Phone'] = volunteers_df['Secondary Phone'].replace({'nan': None})
#     volunteers_df = df.sort_values(by='Attendee Last Name', ascending=True)


    #return riders_df, addon_riders_df, volunteers_df
    return riders_df

# def write_to_excel(file_name, riders_df, addon_riders_df, volunteers_df):
#     with ExcelWriter(file_name) as excel_writer:
#         excel_writer.write_dfs_to_excel(Riders=riders_df, Addons=addon_riders_df, Volunteers=volunteers_df)
def write_to_excel(file_name, riders_df):
    with ExcelWriter(file_name) as excel_writer:
        excel_writer.write_dfs_to_excel(Riders=riders_df)


if __name__ == '__main__':
    formatted_date = get_formatted_date()

    path = 'imports/'
    latest_file = get_latest_file(path)

    #riders_df, addon_riders_df, volunteers_df = process_dataframes(latest_file)
    riders_df = process_dataframes(latest_file)

    file_name = f"Utica_RFMC_{formatted_date}.xlsx"
    #write_to_excel(file_name, riders_df, addon_riders_df, volunteers_df)
    write_to_excel(file_name, riders_df)
