import jdatetime
from django.test import TestCase
import os, pandas


# Create your tests here.
# def save_stock_data_in_db(stock, start_date, end_date):
#     folder = os.getcwd() + f"\\{stock}"
#     print(os.getcwd())
#     files = os.listdir(folder)
#     # Filter for .csv files
#     csv_files = [file for file in files if file.endswith('.csv')]
#
#     # Check if there is exactly one CSV file
#     if len(csv_files) == 1:
#         csv_file_path = os.path.join(folder, csv_files[0])
#         # Read the CSV file using pandas
#         df = pandas.read_csv(csv_file_path)
#         stock_dates_gr = df['<DTYYYYMMDD>'].dropna().values
#         stock_dates = []
#         for i in stock_dates_gr:
#             year = int(str(i)[:4])
#             month = int(str(i)[4:6])
#             day = int(str(i)[6:])
#             jdate = jdatetime.datetime.fromgregorian(day=day, month=month, year=year)
#             i = f"{jdate.strftime('%Y')}{jdate.strftime('%m')}{jdate.strftime('%d')}"
#             stock_dates.append(i)
#
#         stock_returns = df['<CLOSE>'].dropna().values
#
#     else:
#         print("CSV file is not unique")
#
#
# save_stock_data_in_db("كارا", "14030801", "14030819")
# today_year = jdatetime.datetime.now().strftime("%Y")
# today_month = jdatetime.datetime.now().strftime("%m")
# today_day = jdatetime.datetime.now().strftime("%d")
# print(today_month)