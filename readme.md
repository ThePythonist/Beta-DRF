# Stock Beta Coefficient API

This project provides an API for fetching stock and market prices of Iran’s Stock Market, calculating returns, and
determining the beta value for each stock within a specified timeframe.

## Design Decisions

- **Framework**: Django REST Framework was chosen for its robust features and ease of use in building REST APIs.
- **Data Storage**: A relational database (e.g., PostgreSQL, SQLite) is used to store stock and market data for
  efficient querying and data integrity.
- **Data Fetching**: Selenium is utilized for web scraping to fetch live stock and market data, allowing for up-to-date
  calculations of beta values.
- **Date Handling**: Jalali dates are used for consistency in a Persian context, leveraging the `jdatetime` library for
  conversions and validations.

## Features

- Fetch historical stock and market data using web scraping.
- Calculate the beta coefficient for stocks based on historical prices.
- Store and retrieve stock and market data from a database.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
    - [Get Beta Coefficient](#get-beta-coefficient)
- [Caching System](#caching-system)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ThePythonist/Beta-DRF.git
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r req.txt
   ```

4. Set up the database:
    - (Optional) Update your `settings.py` with the desired database configuration.
    - Run migrations:
      ```bash
      python manage.py migrate
      ```

5. Set up Selenium WebDriver:
    - Download the ChromeDriver that matches your Chrome version.
    - Update the path in `scrape.py` where `webdriver.Chrome(service=Service(''))` is called.

## Usage

- Start the development server:
  ```bash
  python manage.py runserver
  ```

- Access the API at `http://127.0.0.1:8000/api/v1/beta/`.

## API Endpoints

### Get Beta Coefficient

- **URL**: `/api/v1/beta/`
- **Method**: `GET`
- **Authentication**: Basic Auth (username and password required)
- **Query Parameters**:
    - `stock_name`: Name of the stock (required) - The Persian name of the stock for which you want to calculate beta.
    - `start_date`: Start date in Jalali format (YYYYMMDD) (required) - The starting date for the historical data range.
    - `end_date`: End date in Jalali format (YYYYMMDD) (required) - The ending date for the historical data range.

#### Example Postman Request

1. Open Postman.
2. Set the request type to `GET`.
3. Enter the URL: `http://127.0.0.1:8000/api/v1/beta/?stock_name=کارا&start_date=13870914&end_date=14011201`.
4. Go to the "Authorization" tab.
5. Select "Basic Auth" and enter your username and password.
6. Click `Send`.

#### Example Response

```json
{
  "id": 1,
  "stock_name": "کارا",
  "start_date": "13870914",
  "end_date": "14011201",
  "value": 1.25
}
```

## Caching System

The application implements a caching system to optimize the retrieval of historical stock and market data. This is
achieved through:

- **Database Storage**: Once historical data is fetched using Selenium, it is stored in the database, reducing the need
  for repeated web scraping for the same data.
- **Conditional Fetching**: Before fetching new data, the application checks whether the required data already exists in
  the database for the specified dates. If data is available, it retrieves it directly, improving response time and
  reducing server load.
- **Data Expiry**: The cached data can have a defined expiration period, ensuring that the information remains
  up-to-date. This can be configured based on your requirements, allowing for a balance between data freshness and
  resource efficiency.

## Logging

Custom logging is implemented to monitor the API response times and errors.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
