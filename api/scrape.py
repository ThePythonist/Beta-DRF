from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from .logging_conf import make_log
import selenium.common
import time
import os
import pandas
import numpy


def fetch_stock_historical_data(stock, start_date, end_date):

    already_fetched = f"api/{stock}/{stock}-{start_date}-{end_date}.xls"
    if stock == "شاخص كل":
        pass
    else:
        already_fetched += "x"

    if not os.path.exists(already_fetched):
        # Set Chrome options
        chrome_options = webdriver.ChromeOptions()
        download_dir = os.getcwd() + f"\\api\\{stock}"

        # Create a ChromeOptions object
        chrome_options = webdriver.ChromeOptions()
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
        else:
            url = 'https://fipiran.com/DataService/TradeIndex'

        try:
            driver.get(url)  # Replace with your target URL
            time.sleep(3)  # Wait for the elements to load
        except selenium.common.exceptions.WebDriverException:
            make_log('error', 'failed to get the web page')
            print('failed to get the web page')
            # print("Connection error. Make sure you are connected to internet and not using VPN. Trying again...")
            driver.quit()
            fetch_stock_historical_data(stock, start_date, end_date)

        try:
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
        except selenium.common.exceptions.NoSuchElementException:
            make_log('error', 'failed to get the web page elements')
            print('failed to get the web page elements')
            # print("Connection error. Make sure you are connected to internet and not using VPN. Trying again...")
            driver.quit()
            fetch_stock_historical_data(stock, start_date, end_date)

        time.sleep(2)

        if stock == 'شاخص كل':
            # Rename the downloaded file
            old_filename = os.path.join(download_dir, 'IndexData.xls')  # Change this to the expected filename
            new_filename = os.path.join(download_dir, f'{stock}-{start_date}-{end_date}.xls')  # Desired new filename

            # Rename the file if it exists
            if os.path.exists(old_filename):
                os.rename(old_filename, new_filename)
                driver.quit()
        else:
            # Rename the downloaded file
            old_filename = os.path.join(download_dir, 'symbolData.xls')  # Change this to the expected filename
            new_filename = os.path.join(download_dir, f'{stock}-{start_date}-{end_date}.xls')  # Desired new filename

            # Rename the file if it exists
            if os.path.exists(old_filename):
                os.rename(old_filename, new_filename)

            make_log('info', f'created {stock}.xls')

            # Create the cleaned file out of stock file and market-file
            create_clean_file(stock, start_date, end_date)
            make_log('info', f'created {stock}.xlsx')

            # Delete the .xls (unclean) stock file
            if os.path.exists(new_filename):
                os.remove(new_filename)  # Delete the file
                make_log('info', f'deleted {new_filename}')
            else:
                make_log('error', f'{new_filename} doesnt exist')
            driver.quit()


def create_clean_file(stock, start_date, end_date):
    if not os.path.exists(f"api/{stock}/{stock}-{start_date}-{end_date}.xlsx"):
        market_file = f"api/شاخص كل/شاخص كل-{start_date}-{end_date}.xls"
        stock_file = f"api/{stock}/{stock}-{start_date}-{end_date}.xls"

        market_df = pandas.read_html(market_file)
        market_returns = market_df[0]['Value'].dropna().values
        market_returns = market_returns.tolist()
        # print(market_returns)
        try:
            stock_df = pandas.read_html(stock_file)

            stock_returns = stock_df[0]['ClosePrice'].dropna().values
            stock_returns = stock_returns.tolist()
            # print(stock_returns)

            # Create a DataFrame from the two lists
            data = {
                'stock_returns': stock_returns,
                'market_returns': market_returns,
            }
            combined_df = pandas.DataFrame(data)

            # Save the clean DataFrame to an Excel file
            output_file = f"api/{stock}/{stock}-{start_date}-{end_date}.xlsx"
            combined_df.to_excel(output_file, index=False)

            make_log('info', f'Created {output_file}')

        except ValueError:
            print("BUG HERE : scrape.py line 156")
            # Stock-historical-data file is damaged or not downloaded so download it first
            # fetch_stock_historical_data(stock, start_date, end_date)


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
