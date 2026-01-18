"""
CoinMarketCap Web Scraper Module
Handles web scraping of cryptocurrency data using Selenium and BeautifulSoup
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict
from contextlib import contextmanager

from config import (
    COINMARKETCAP_URL,
    SCROLL_PAUSE_TIME,
    SCROLL_STEP,
    MAX_SCROLL_ATTEMPTS,
    EXPLICIT_WAIT_TIMEOUT,
    CHROME_OPTIONS,
    CHROME_EXPERIMENTAL_OPTIONS
)

logger = logging.getLogger(__name__)


@contextmanager
def get_chrome_driver():
    """
    Context manager for Chrome WebDriver to ensure proper cleanup.
    
    Yields:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    options = Options()
    
    # Add command line options
    for option in CHROME_OPTIONS:
        options.add_argument(option)
    
    # Add experimental options
    for key, value in CHROME_EXPERIMENTAL_OPTIONS.items():
        options.add_experimental_option(key, value)
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        logger.info("Chrome WebDriver initialized successfully")
        yield driver
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed successfully")


def scroll_to_load_content(driver: webdriver.Chrome, max_scrolls: int = MAX_SCROLL_ATTEMPTS) -> None:
    """
    Scroll the page to load dynamic content.
    
    Args:
        driver: Selenium WebDriver instance
        max_scrolls: Maximum number of scroll attempts to prevent infinite loops
    """
    scroll_attempts = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    logger.info("Starting page scroll to load dynamic content")
    
    while scroll_attempts < max_scrolls:
        # Smooth scroll to bottom
        for i in range(0, last_height, SCROLL_STEP):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(SCROLL_PAUSE_TIME)
        
        # Wait for new content to load
        time.sleep(1)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logger.info("Reached end of page")
            break
        
        last_height = new_height
        scroll_attempts += 1
        logger.info(f"Scroll attempt {scroll_attempts}/{max_scrolls}")
    
    logger.info("Finished scrolling")


def parse_crypto_data(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """
    Parse cryptocurrency data from BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup object containing the page HTML
        
    Returns:
        List of dictionaries containing cryptocurrency information
    """
    crypto_data = []
    
    table = soup.find('table', {'class': 'cmc-table'})
    if not table:
        logger.error("Could not find cryptocurrency table")
        return crypto_data
    
    rows = table.find_all('tr')
    logger.info(f"Found {len(rows)-1} cryptocurrency rows (excluding header)")
    
    for row in rows[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) >= 10:
            try:
                crypto_info = {
                    'rank': cols[1].text.strip(),
                    'name': cols[2].text.strip(),
                    'price': cols[3].text.strip(),
                    '1h_change': cols[4].text.strip(),
                    '24h_change': cols[5].text.strip(),
                    '7d_change': cols[6].text.strip(),
                    'market_cap': cols[7].text.strip(),
                    '24h_volume': cols[8].text.strip(),
                    'circulating_supply': cols[9].text.strip()
                }
                crypto_data.append(crypto_info)
            except (IndexError, AttributeError) as e:
                logger.warning(f"Error parsing row: {e}")
                continue
    
    return crypto_data


def scrape_coinmarketcap() -> List[Dict[str, str]]:
    """
    Main function to scrape cryptocurrency data from CoinMarketCap.
    
    Returns:
        List of dictionaries containing cryptocurrency information
    """
    try:
        with get_chrome_driver() as driver:
            logger.info(f"Navigating to {COINMARKETCAP_URL}")
            driver.get(COINMARKETCAP_URL)
            
            # Wait for table to be present
            try:
                WebDriverWait(driver, EXPLICIT_WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cmc-table"))
                )
                logger.info("Table loaded successfully")
            except TimeoutException:
                logger.error("Timeout waiting for table to load")
                return []
            
            # Scroll to load all content
            scroll_to_load_content(driver)
            
            # Parse the page
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
        # Parse crypto data
        crypto_data = parse_crypto_data(soup)
        logger.info(f"Successfully scraped {len(crypto_data)} cryptocurrencies")
        
        return crypto_data
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Starting CoinMarketCap scraper...")
    data = scrape_coinmarketcap()
    
    if data:
        print(f"\nSuccessfully scraped {len(data)} cryptocurrencies")
        print("\nFirst 5 results:")
        for crypto in data[:5]:
            print(f"  {crypto['rank']:>4} | {crypto['name']:<20} | {crypto['price']:<15}")
    else:
        print("Failed to scrape data")
