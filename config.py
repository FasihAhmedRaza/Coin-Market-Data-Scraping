"""
Configuration file for CoinMarketCap Scraper
"""

COINMARKETCAP_URL = 'https://coinmarketcap.com/'
SCROLL_PAUSE_TIME = 0.5
SCROLL_STEP = 300
MAX_SCROLL_ATTEMPTS = 5
EXPLICIT_WAIT_TIMEOUT = 10

# SQL Server Configuration
DB_CONFIG = {
    'server': 'localhost',  
    'database': 'CryptoData',  
    'username': '',  
    'password': '', 
    'driver': '{ODBC Driver 17 for SQL Server}'
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'crypto_scraper.log'

# Chrome WebDriver Options
CHROME_OPTIONS = [
    "--start-maximized",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled"
]

CHROME_EXPERIMENTAL_OPTIONS = {
    "excludeSwitches": ["enable-automation"],
    "useAutomationExtension": False
}

# Table Schema
TABLE_NAME = 'CryptoCurrency'
