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
        market_df = pandas.read_html(market_file)

        market_dates = market_df[0]['dateissue'].dropna().values
        market_dates = market_dates.tolist()

        market_returns = market_df[0]['Value'].dropna().values
        market_returns = market_returns.tolist()

        for a, b in zip(market_dates, market_returns):
            MarketIndex.objects.create(
                date=a,
                price=b
            )


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
        stock_dates_gr = df['<DTYYYYMMDD>'].dropna().values
        stock_dates = []
        for i in stock_dates_gr:
            year = int(str(i)[:4])
            month = int(str(i)[4:6])
            day = int(str(i)[6:])
            jdate = jdatetime.datetime.fromgregorian(day=day, month=month, year=year)
            i = f"{jdate.strftime('%Y')}{jdate.strftime('%m')}{jdate.strftime('%d')}"
            stock_dates.append(i)

        stock_returns = df['<CLOSE>'].dropna().values

        for a, b in zip(stock_dates, stock_returns):
            Stock.objects.create(
                stock_name=stock,
                date=a,
                price=b
            )

    else:
        print("CSV file is not unique")


def calculate_beta(stock, start_date, end_date):
    file_name = f"api/{stock}/{stock}-{start_date}-{end_date}.xlsx"
    df = pandas.read_excel(file_name)

    # Drop rows from dataframe where either 'STOCK' or 'MARKET' are NaN
    df = df.dropna(subset=['stock_returns', 'market_returns'])

    # Extract stock and market returns
    stock_returns = df['stock_returns'].values  # Convert to numpy array
    market_returns = df['market_returns'].values  # Convert to numpy array

    # Prepare the data dictionary
    data = {
        'stock_returns': stock_returns.tolist(),
        'market_returns': market_returns.tolist()
    }

    # Calculate beta
    covariance = numpy.cov(data['stock_returns'], data['market_returns'])[0][1]
    # ddof=1 for sample variance
    market_variance = numpy.var(data['market_returns'], ddof=1)
    beta = covariance / market_variance

    return beta
