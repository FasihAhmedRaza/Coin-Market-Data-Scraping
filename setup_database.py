"""
SQL Server Database Setup Script
Run this to create the database and table
"""

CREATE_DATABASE_SQL = """
-- Create database if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CryptoData')
BEGIN
    CREATE DATABASE CryptoData;
    PRINT 'Database CryptoData created successfully';
END
ELSE
BEGIN
    PRINT 'Database CryptoData already exists';
END
GO

-- Use the database
USE CryptoData;
GO
"""

CREATE_TABLE_SQL = """
-- Create CryptoCurrency table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CryptoCurrency' AND xtype='U')
BEGIN
    CREATE TABLE CryptoCurrency (
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
    );
    
    PRINT 'Table CryptoCurrency created successfully';
END
ELSE
BEGIN
    PRINT 'Table CryptoCurrency already exists';
END
GO
"""

USEFUL_QUERIES = """
-- ========================================
-- USEFUL SQL QUERIES FOR DATA ANALYSIS
-- ========================================

-- 1. View all data ordered by rank
SELECT * FROM CryptoCurrency 
ORDER BY scraped_at DESC, rank;

-- 2. Get latest scrape results (top 10)
SELECT TOP 10 
    rank, name, price, one_hour_change, twenty_four_hour_change,
    seven_day_change, market_cap, volume_24h, scraped_at
FROM CryptoCurrency
ORDER BY scraped_at DESC, rank;

-- 3. Count records by scrape date
SELECT 
    CAST(scraped_at AS DATE) as scrape_date,
    COUNT(*) as total_records
FROM CryptoCurrency
GROUP BY CAST(scraped_at AS DATE)
ORDER BY scrape_date DESC;

-- 4. Top 10 cryptocurrencies by market cap (latest scrape)
SELECT TOP 10
    rank, name, price, market_cap, volume_24h, twenty_four_hour_change
FROM CryptoCurrency
WHERE scraped_at = (SELECT MAX(scraped_at) FROM CryptoCurrency)
ORDER BY rank;

-- 5. Search specific cryptocurrency (e.g., Bitcoin)
SELECT * 
FROM CryptoCurrency
WHERE name LIKE '%Bitcoin%'
ORDER BY scraped_at DESC;

-- 6. Get historical data for a specific coin
SELECT 
    name, price, market_cap, twenty_four_hour_change, scraped_at
FROM CryptoCurrency
WHERE name = 'Bitcoin'
ORDER BY scraped_at DESC;

-- 7. Top gainers in last 24 hours (from latest scrape)
SELECT TOP 10
    rank, name, price, twenty_four_hour_change, market_cap
FROM CryptoCurrency
WHERE scraped_at = (SELECT MAX(scraped_at) FROM CryptoCurrency)
    AND twenty_four_hour_change NOT LIKE '%-%'
ORDER BY CAST(REPLACE(REPLACE(twenty_four_hour_change, '%', ''), '+', '') AS FLOAT) DESC;

-- 8. Top losers in last 24 hours (from latest scrape)
SELECT TOP 10
    rank, name, price, twenty_four_hour_change, market_cap
FROM CryptoCurrency
WHERE scraped_at = (SELECT MAX(scraped_at) FROM CryptoCurrency)
    AND twenty_four_hour_change LIKE '%-%'
ORDER BY CAST(REPLACE(REPLACE(twenty_four_hour_change, '%', ''), '-', '') AS FLOAT) DESC;

-- 9. Average prices over time for top 5 cryptos
SELECT 
    name,
    COUNT(*) as scrape_count,
    MIN(CAST(scraped_at AS DATE)) as first_date,
    MAX(CAST(scraped_at AS DATE)) as last_date
FROM CryptoCurrency
WHERE rank <= 5
GROUP BY name
ORDER BY name;

-- 10. Delete old data (keep last 30 days)
DELETE FROM CryptoCurrency
WHERE scraped_at < DATEADD(day, -30, GETDATE());

-- 11. Database statistics
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT name) as unique_cryptos,
    COUNT(DISTINCT CAST(scraped_at AS DATE)) as total_scrape_days,
    MIN(scraped_at) as first_scrape,
    MAX(scraped_at) as last_scrape
FROM CryptoCurrency;
"""

if __name__ == "__main__":
    print("SQL Server Setup Scripts")
    print("=" * 60)
    print("\n1. CREATE DATABASE:")
    print(CREATE_DATABASE_SQL)
    print("\n2. CREATE TABLE:")
    print(CREATE_TABLE_SQL)
    print("\n3. USEFUL QUERIES:")
    print(USEFUL_QUERIES)
    
    # Save to file
    with open('setup_database.sql', 'w') as f:
        f.write("-- SQL Server Database Setup Script\n")
        f.write("-- CoinMarketCap Cryptocurrency Scraper\n")
        f.write("-- " + "=" * 58 + "\n\n")
        f.write(CREATE_DATABASE_SQL)
        f.write("\n\n")
        f.write(CREATE_TABLE_SQL)
        f.write("\n\n")
        f.write(USEFUL_QUERIES)
    
    print("\n" + "=" * 60)
    print("✅ SQL scripts saved to 'setup_database.sql'")
    print("Run this file in SQL Server Management Studio (SSMS)")
