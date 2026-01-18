"""
Utility Functions for Data Analysis and Export
"""

import pandas as pd
import logging
from typing import Optional
from database import get_sql_connection, TABLE_NAME

logger = logging.getLogger(__name__)


def query_to_dataframe(query: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    
    Args:
        query: SQL query string
        
    Returns:
        pandas DataFrame with query results
    """
    try:
        with get_sql_connection() as connection:
            df = pd.read_sql(query, connection)
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return pd.DataFrame()


def get_latest_crypto_dataframe(limit: int = 100) -> pd.DataFrame:
    """
    Get latest cryptocurrency data as a DataFrame.
    
    Args:
        limit: Number of records to retrieve
        
    Returns:
        pandas DataFrame with latest crypto data
    """
    query = f"""
    SELECT TOP ({limit})
        rank, name, price, one_hour_change as '1h_change',
        twenty_four_hour_change as '24h_change', seven_day_change as '7d_change',
        market_cap, volume_24h, circulating_supply, scraped_at
    FROM {TABLE_NAME}
    ORDER BY scraped_at DESC, rank
    """
    return query_to_dataframe(query)


def export_to_csv(filename: str = 'crypto_data.csv', limit: Optional[int] = None) -> bool:
    """
    Export cryptocurrency data to CSV file.
    
    Args:
        filename: Output CSV filename
        limit: Number of records to export (None for all)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        df = get_latest_crypto_dataframe(limit if limit else 10000)
        if not df.empty:
            df.to_csv(filename, index=False)
            logger.info(f"Data exported to {filename}")
            print(f"✅ Exported {len(df)} records to {filename}")
            return True
        else:
            logger.warning("No data to export")
            return False
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False


def export_to_excel(filename: str = 'crypto_data.xlsx', limit: Optional[int] = None) -> bool:
    """
    Export cryptocurrency data to Excel file.
    
    Args:
        filename: Output Excel filename
        limit: Number of records to export (None for all)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        df = get_latest_crypto_dataframe(limit if limit else 10000)
        if not df.empty:
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"Data exported to {filename}")
            print(f"✅ Exported {len(df)} records to {filename}")
            return True
        else:
            logger.warning("No data to export")
            return False
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        print(f"❌ Error: {e}")
        print("Hint: Install openpyxl with: pip install openpyxl")
        return False


def get_top_gainers(limit: int = 10) -> pd.DataFrame:
    """
    Get top gaining cryptocurrencies based on 24h change.
    
    Args:
        limit: Number of top gainers to retrieve
        
    Returns:
        pandas DataFrame with top gainers
    """
    query = f"""
    SELECT TOP ({limit})
        rank, name, price, twenty_four_hour_change as '24h_change',
        market_cap, volume_24h
    FROM {TABLE_NAME}
    WHERE scraped_at = (SELECT MAX(scraped_at) FROM {TABLE_NAME})
        AND twenty_four_hour_change NOT LIKE '%-%'
    ORDER BY 
        CAST(REPLACE(REPLACE(twenty_four_hour_change, '%', ''), '+', '') AS FLOAT) DESC
    """
    return query_to_dataframe(query)


def get_top_losers(limit: int = 10) -> pd.DataFrame:
    """
    Get top losing cryptocurrencies based on 24h change.
    
    Args:
        limit: Number of top losers to retrieve
        
    Returns:
        pandas DataFrame with top losers
    """
    query = f"""
    SELECT TOP ({limit})
        rank, name, price, twenty_four_hour_change as '24h_change',
        market_cap, volume_24h
    FROM {TABLE_NAME}
    WHERE scraped_at = (SELECT MAX(scraped_at) FROM {TABLE_NAME})
        AND twenty_four_hour_change LIKE '%-%'
    ORDER BY 
        CAST(REPLACE(REPLACE(twenty_four_hour_change, '%', ''), '-', '') AS FLOAT) DESC
    """
    return query_to_dataframe(query)


def search_crypto(name: str) -> pd.DataFrame:
    """
    Search for a specific cryptocurrency by name.
    
    Args:
        name: Cryptocurrency name to search for
        
    Returns:
        pandas DataFrame with search results
    """
    query = f"""
    SELECT 
        rank, name, price, one_hour_change as '1h_change',
        twenty_four_hour_change as '24h_change', seven_day_change as '7d_change',
        market_cap, volume_24h, scraped_at
    FROM {TABLE_NAME}
    WHERE name LIKE '%{name}%'
    ORDER BY scraped_at DESC, rank
    """
    return query_to_dataframe(query)


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Testing utility functions...\n")
    
    # Get latest data
    print("📊 Latest 5 Cryptocurrencies:")
    df = get_latest_crypto_dataframe(5)
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("No data available")
    
    # Export to CSV
    print("\n📁 Exporting to CSV...")
    export_to_csv('latest_crypto_data.csv', 50)
