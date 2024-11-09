from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from .customlogs import make_log
from .models import *
import selenium.common
import time
import os
import pandas
import numpy
import jdatetime
from django.db import transaction

funds = [
    {'name': "كارا", "type": "درآمد ثابت", "code": "71843282162462661"},
    {'name': "آگاس", "type": "سهامی", "code": "33887145736684266"},
    {'name': "تمشك", "type": "صندوق در صندوق", "code": "53145304508578701"},
]


def fetch_stock_historical_data(stock, start_date, end_date):
    if stock == "شاخص كل":
        already_fetched = f"api/{stock}/{stock}-{start_date}-{end_date}.xls"
    else:
        already_fetched = f"api/{stock}/"

    if not os.path.exists(already_fetched):
        # Set Chrome options
        chrome_options = webdriver.ChromeOptions()
        download_dir = os.getcwd() + f"\\api\\{stock}"

        prefs = {
            "download.default_directory": download_dir,  # Set download directory to Desktop
            "download.prompt_for_download": False,  # Disable download prompt
            "download.directory_upgrade": True,  # Allow directory upgrade
            "safebrowsing.enabled": True  # Enable safe browsing
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Initialize the WebDriver
        driver = webdriver.Chrome(service=Service(''), options=chrome_options)

        # Open the web page
        if stock == 'شاخص كل':
            url = 'https://fipiran.com/DataService/IndexIndex'
            try:
                driver.get(url)  # Replace with your target URL
                time.sleep(3)  # Wait for the elements to load

                ok_button = driver.find_element(
                    By.XPATH, '/html/body/div[4]/div/div[3]/button[1]'
                )  # Update selector

                ok_button.click()

                # Fill the input fields and click the download button (same as previous example)
                symbol = driver.find_element(By.XPATH,
                                             '/html/body/section[2]/div/form/div/div[1]/input[1]')  # Update selector
                startdate = driver.find_element(By.XPATH,
                                                '/html/body/section[2]/div/form/div/div[2]/input')  # Update selector
                enddate = driver.find_element(By.XPATH,
                                              '/html/body/section[2]/div/form/div/div[3]/input')  # Update selector

                symbol.send_keys(stock)
                time.sleep(1)

                suggestions = driver.find_elements(By.CLASS_NAME, 'ui-menu-item')

                # Iterate through the suggested items and click on the one we are looking for
                for item in suggestions:
                    if item.text == stock:
                        item.click()

                startdate.send_keys(start_date)
                enddate.send_keys(end_date)

                time.sleep(3)

                download_button = driver.find_element(
                    By.XPATH, '/html/body/section[2]/div/form/div/div[4]/input'
                )  # Update selector

                download_button.click()
                time.sleep(3)
            except selenium.common.exceptions.NoSuchElementException:
                make_log('error', 'Failed to get the web page elements')
                print('Failed to get the web page elements')
                # print("Connection error. Make sure you are connected to internet and not using VPN. Trying again...")
                driver.quit()
                fetch_stock_historical_data(stock, start_date, end_date)

            # Rename the downloaded file
            old_filename = os.path.join(download_dir, 'IndexData.xls')  # Change this to the expected filename
            new_filename = os.path.join(download_dir, f'{stock}-{start_date}-{end_date}.xls')  # Desired new filename

            # Rename the file if it exists
            if os.path.exists(old_filename):
                os.rename(old_filename, new_filename)
                driver.quit()

            # Save market index historical data in local DB for future requests
            save_market_data_in_db(stock, start_date, end_date)

        else:
            for i in funds:
                if i["name"] == stock:
                    code = i["code"]
                    break
            else:
                print("Fund not found")

            url = f"https://www.tsetmc.com/instInfo/{code}"

            try:
                driver.get(url)  # Replace with your target URL
                time.sleep(4)  # Wait for the elements to load

                download_button = driver.find_element(
                    By.XPATH, '/html/body/div/div/div[2]/div[3]/div[1]/div[2]/div[4]'
                )  # Update selector

                download_button.click()
                time.sleep(3)  # Wait for the elements to load

                save_stock_data_in_db(stock, start_date, end_date)

            except selenium.common.exceptions.WebDriverException:
                print('Failed to get the web page')
                fetch_stock_historical_data(stock, start_date, end_date)
                driver.quit()


def save_market_data_in_db(stock, start_date, end_date):
    if stock == "شاخص كل":
        market_file = f"api/شاخص كل/شاخص كل-{start_date}-{end_date}.xls"
        # Read the HTML file which returns a list of DataFrames
        market_df_list = pandas.read_html(market_file)

        # Get the first DataFrame from the list
        market_df = market_df_list[0]

        # Ensure 'dateissue' and 'Value' columns are in the DataFrame
        market_dates = market_df['dateissue'].dropna().values
        market_returns = market_df['Value'].dropna().values

        # Prepare the list of MarketIndex objects to be created
        market_entries = [
            MarketIndex(date=row['dateissue'], price=row['Value'])
            for _, row in market_df.iterrows()
        ]

        # Bulk insert all entries at once in a transaction for efficiency
        with transaction.atomic():
            MarketIndex.objects.bulk_create(market_entries)


def save_stock_data_in_db(stock, start_date, end_date):
    folder = os.getcwd() + f"\\api\\{stock}"
    files = os.listdir(folder)

    # Filter for .csv files
    csv_files = [file for file in files if file.endswith('.csv')]

    # Check if there is exactly one CSV file
    if len(csv_files) == 1:
        csv_file_path = os.path.join(folder, csv_files[0])

        # Read the CSV file using pandas
        df = pandas.read_csv(csv_file_path)

        # Process the dates and prices
        stock_dates_gr = df['<DTYYYYMMDD>'].dropna().values
        stock_dates = []
        for i in stock_dates_gr:
            year = int(str(i)[:4])
            month = int(str(i)[4:6])
            day = int(str(i)[6:])
            jdate = jdatetime.datetime.fromgregorian(day=day, month=month, year=year)
            formatted_date = f"{jdate.strftime('%Y')}{jdate.strftime('%m')}{jdate.strftime('%d')}"
            stock_dates.append(formatted_date)

        stock_returns = df['<CLOSE>'].dropna().values

        # Prepare list of Stock instances to bulk insert
        stock_data = [
            Stock(stock_name=stock, date=a, price=b)
            for a, b in zip(stock_dates, stock_returns)
        ]

        # Wrap the bulk insert in a transaction for atomicity
        with transaction.atomic():
            Stock.objects.bulk_create(stock_data)

    else:
        print("CSV file is not unique")


def calculate_beta(stock, start_date, end_date):
    stock_data = Stock.objects.filter(stock_name=stock)
    market_data = MarketIndex.objects.all()

    stock_returns = []
    market_returns = []

    for stock_entry in stock_data:
        stock_date = str(stock_entry.date)  # Keep the date as a string (e.g., '20240801')

        # Check if the stock date is within the range (compare as strings)
        if start_date <= stock_date <= end_date:
            # Ensure the market data corresponds to the same date
            market_entry = market_data.filter(date=stock_entry.date).first()
            if market_entry:
                stock_returns.append(stock_entry.price)
                market_returns.append(market_entry.price)

    # If either list is empty, return None or handle the error
    if len(stock_returns) == 0 or len(market_returns) == 0:
        # return None
        print('*******bug here*******')

    # Convert lists to numpy arrays
    stock_returns = numpy.array(stock_returns)
    market_returns = numpy.array(market_returns)

    # Calculate covariance and market variance
    covariance = numpy.cov(stock_returns, market_returns)[0][1]
    market_variance = numpy.var(market_returns, ddof=1)

    # Calculate Beta
    beta = covariance / market_variance

    return beta
