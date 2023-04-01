import pandas as pd
import xlsxwriter
import openpyxl
import re

# class ExcelWriter:
#     def __init__(self, file_name):
#         self.file_name = file_name
#         self.writer = pd.ExcelWriter(self.file_name, engine='xlsxwriter')

#     def __enter__(self):
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.writer.save()

#     def write_dfs_to_excel(self, **dfs):
#         for sheet_name, df in dfs.items():
#             df.to_excel(self.writer, sheet_name=sheet_name, index=False)
#             worksheet = self.writer.sheets[sheet_name]
#             self.adjust_column_width(worksheet, df)

#     def adjust_column_width(self, worksheet, df):
#         for idx, col in enumerate(df.columns):
#             max_len = max(
#                 df[col].astype(str).map(len).max(),  # length of the longest data
#                 len(str(col))  # length of the column header
#             )
#             worksheet.set_column(idx, idx, max_len + 1)  # add some padding

class ExcelWriter:
    def __init__(self, file_name):
        self.file_name = file_name
        self.writer = pd.ExcelWriter(self.file_name, engine='xlsxwriter')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.writer.save()

    def write_dfs_to_excel(self, **dfs):
        for sheet_name, df in dfs.items():
            df.to_excel(self.writer, sheet_name=sheet_name, index=False)
            worksheet = self.writer.sheets[sheet_name]
            self.adjust_column_width(worksheet, df)
            # self.apply_date_format(worksheet, df, 'Created Date', 'MM/DD/YYYY')
            # self.apply_date_format(worksheet, df, 'Birth Date', 'MM/DD/YYYY')

    def adjust_column_width(self, worksheet, df):
        for idx, col in enumerate(df.columns):
            max_len = max(
                df[col].astype(str).map(len).max(),
                len(str(col))
            )
            worksheet.set_column(idx, idx, max_len + 1)

    def apply_date_format(self, worksheet, df, date_col, date_format):
        if date_col not in df.columns:
            return

        col_idx = df.columns.get_loc(date_col)
        date_fmt = self.writer.book.add_format({'num_format': date_format})

        for row_idx, value in enumerate(df[date_col], start=1):  # start=1 to skip header
            if pd.notnull(value):
                worksheet.write(row_idx, col_idx, value, date_fmt)



class DataProcessor:
    @staticmethod
    def format_phone_number(number):
        # Check if the input is a string or bytes-like object
        if not isinstance(number, (str, bytes)):
            return number

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