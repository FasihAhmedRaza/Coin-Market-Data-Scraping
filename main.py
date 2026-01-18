"""
Main Application Entry Point
CoinMarketCap Cryptocurrency Scraper with SQL Server Integration
"""

import logging
from scraper import scrape_coinmarketcap
from database import save_to_sql_server
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def main():
    """Main application function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Scrape data
        logger.info("Starting cryptocurrency scraping...")
        crypto_data = scrape_coinmarketcap()
        
        if not crypto_data:
            logger.error("Failed to scrape data")
            return
        
        logger.info(f"Successfully scraped {len(crypto_data)} cryptocurrencies")
        
        # Save to database
        logger.info("Saving data to SQL Server...")
        if save_to_sql_server(crypto_data):
            logger.info(f"Successfully saved {len(crypto_data)} records to database")
        else:
            logger.error("Failed to save data to database")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
