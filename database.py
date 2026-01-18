"""
Database Module for SQL Server Operations
Handles all database connections, table creation, and data operations
"""

import pyodbc
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Optional
import logging

from config import DB_CONFIG, TABLE_NAME

logger = logging.getLogger(__name__)


@contextmanager
def get_sql_connection():
    """
    Context manager for SQL Server connection to ensure proper cleanup.
    
    Yields:
        pyodbc.Connection: Active database connection
    """
    connection = None
    try:
        # Build connection string
        if DB_CONFIG['username']:
            # SQL Server Authentication
            conn_str = (
                f"DRIVER={DB_CONFIG['driver']};"
                f"SERVER={DB_CONFIG['server']};"
                f"DATABASE={DB_CONFIG['database']};"
                f"UID={DB_CONFIG['username']};"
                f"PWD={DB_CONFIG['password']}"
            )
        else:
            # Windows Authentication
            conn_str = (
                f"DRIVER={DB_CONFIG['driver']};"
                f"SERVER={DB_CONFIG['server']};"
                f"DATABASE={DB_CONFIG['database']};"
                f"Trusted_Connection=yes;"
            )
        
        connection = pyodbc.connect(conn_str)
        logger.info("Database connection established")
        yield connection
        
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed")


def create_crypto_table(cursor: pyodbc.Cursor) -> None:
    """
    Create the cryptocurrency table if it doesn't exist.
    
    Args:
        cursor: Database cursor object
    """
    create_table_query = f"""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{TABLE_NAME}' AND xtype='U')
    CREATE TABLE {TABLE_NAME} (
        id INT IDENTITY(1,1) PRIMARY KEY,
        rank INT,
        name NVARCHAR(100),
        price NVARCHAR(50),
        one_hour_change NVARCHAR(20),
        twenty_four_hour_change NVARCHAR(20),
        seven_day_change NVARCHAR(20),
        market_cap NVARCHAR(50),
        volume_24h NVARCHAR(50),
        circulating_supply NVARCHAR(100),
        scraped_at DATETIME DEFAULT GETDATE(),
        INDEX idx_name (name),
        INDEX idx_rank (rank),
        INDEX idx_scraped_at (scraped_at)
    )
    """
    cursor.execute(create_table_query)
    logger.info(f"Table '{TABLE_NAME}' created or already exists")


def insert_crypto_data(connection: pyodbc.Connection, crypto_data: List[Dict[str, str]]) -> int:
    """
    Insert cryptocurrency data into SQL Server table.
    
    Args:
        connection: Active database connection
        crypto_data: List of cryptocurrency dictionaries
        
    Returns:
        Number of rows inserted
    """
    cursor = connection.cursor()
    
    try:
        # Create table if it doesn't exist
        create_crypto_table(cursor)
        connection.commit()
        
        # Prepare insert query
        insert_query = f"""
        INSERT INTO {TABLE_NAME}
        (rank, name, price, one_hour_change, twenty_four_hour_change, 
         seven_day_change, market_cap, volume_24h, circulating_supply, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare data for batch insert
        current_time = datetime.now()
        rows_to_insert = []
        
        for crypto in crypto_data:
            row = (
                int(crypto['rank']) if crypto['rank'].isdigit() else None,
                crypto['name'],
                crypto['price'],
                crypto['1h_change'],
                crypto['24h_change'],
                crypto['7d_change'],
                crypto['market_cap'],
                crypto['24h_volume'],
                crypto['circulating_supply'],
                current_time
            )
            rows_to_insert.append(row)
        
        # Execute batch insert
        cursor.executemany(insert_query, rows_to_insert)
        connection.commit()
        
        rows_inserted = len(rows_to_insert)
        logger.info(f"Successfully inserted {rows_inserted} records into database")
        
        return rows_inserted
        
    except pyodbc.Error as e:
        connection.rollback()
        logger.error(f"Error inserting data: {e}")
        raise
    finally:
        cursor.close()


def save_to_sql_server(crypto_data: List[Dict[str, str]]) -> bool:
    """
    Main function to save cryptocurrency data to SQL Server.
    
    Args:
        crypto_data: List of cryptocurrency dictionaries
        
    Returns:
        True if successful, False otherwise
    """
    if not crypto_data:
        logger.warning("No data to save")
        return False
    
    try:
        with get_sql_connection() as connection:
            rows_inserted = insert_crypto_data(connection, crypto_data)
            logger.info(f"Data save completed: {rows_inserted} rows")
            return True
            
    except Exception as e:
        logger.error(f"Failed to save data to SQL Server: {e}", exc_info=True)
        return False


def get_recent_data(limit: int = 10) -> Optional[List]:
    """
    Retrieve most recent cryptocurrency data from the database.
    
    Args:
        limit: Number of records to retrieve
        
    Returns:
        List of tuples containing cryptocurrency data
    """
    try:
        with get_sql_connection() as connection:
            cursor = connection.cursor()
            
            query = f"""
            SELECT TOP (?) 
                rank, name, price, one_hour_change, twenty_four_hour_change,
                seven_day_change, market_cap, volume_24h, circulating_supply, scraped_at
            FROM {TABLE_NAME}
            ORDER BY scraped_at DESC
            """
            
            cursor.execute(query, limit)
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        return None


def get_crypto_statistics() -> Dict:
    """
    Get statistics about stored cryptocurrency data.
    
    Returns:
        Dictionary with statistics
    """
    stats = {}
    
    try:
        with get_sql_connection() as connection:
            cursor = connection.cursor()
            
            # Total records
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            stats['total_records'] = cursor.fetchone()[0]
            
            # Unique cryptocurrencies
            cursor.execute(f"SELECT COUNT(DISTINCT name) FROM {TABLE_NAME}")
            stats['unique_cryptos'] = cursor.fetchone()[0]
            
            # Date range
            cursor.execute(f"""
                SELECT 
                    MIN(scraped_at) as first_scrape,
                    MAX(scraped_at) as last_scrape
                FROM {TABLE_NAME}
            """)
            row = cursor.fetchone()
            stats['first_scrape'] = row[0]
            stats['last_scrape'] = row[1]
            
            # Scrape count
            cursor.execute(f"""
                SELECT COUNT(DISTINCT CAST(scraped_at AS DATE))
                FROM {TABLE_NAME}
            """)
            stats['total_scrapes'] = cursor.fetchone()[0]
            
            cursor.close()
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
    
    return stats


def delete_old_data(days: int = 30) -> int:
    """
    Delete cryptocurrency data older than specified days.
    
    Args:
        days: Number of days to keep (default: 30)
        
    Returns:
        Number of rows deleted
    """
    try:
        with get_sql_connection() as connection:
            cursor = connection.cursor()
            
            delete_query = f"""
            DELETE FROM {TABLE_NAME}
            WHERE scraped_at < DATEADD(day, ?, GETDATE())
            """
            
            cursor.execute(delete_query, -days)
            rows_deleted = cursor.rowcount
            connection.commit()
            cursor.close()
            
            logger.info(f"Deleted {rows_deleted} old records")
            return rows_deleted
            
    except Exception as e:
        logger.error(f"Error deleting old data: {e}")
        return 0


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Testing database connection...")
    try:
        with get_sql_connection() as conn:
            print("✅ Database connection successful!")
            
        stats = get_crypto_statistics()
        if stats:
            print("\n📊 Database Statistics:")
            print(f"   Total Records: {stats.get('total_records', 0)}")
            print(f"   Unique Cryptos: {stats.get('unique_cryptos', 0)}")
            print(f"   Total Scrapes: {stats.get('total_scrapes', 0)}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
