<!-- 
  CoinMarketCap Scraper - Architecture Diagram for Draw.io
  
  HOW TO USE:
  1. Go to https://app.diagrams.net/ (Draw.io)
  2. Click "File" > "Import from" > "Device"
  3. Select this file (architecture_diagram.drawio)
  4. Edit and customize as needed
  
  OR you can copy the Mermaid diagram below and use it in:
  - GitHub Markdown
  - Mermaid Live Editor (https://mermaid.live/)
  - VS Code with Mermaid extension
-->

# MERMAID DIAGRAM - SYSTEM ARCHITECTURE

```mermaid
graph TB
    subgraph "User Interface"
        A[main.py<br/>Entry Point]
    end
    
    subgraph "Configuration Layer"
        B[config.py<br/>Settings & Config]
    end
    
    subgraph "Business Logic"
        C[scraper.py<br/>Web Scraping]
        D[database.py<br/>Data Persistence]
        E[utils.py<br/>Data Analysis]
    end
    
    subgraph "External Systems"
        F[(SQL Server<br/>CryptoData DB)]
        G[CoinMarketCap<br/>Website]
        H[Chrome<br/>WebDriver]
    end
    
    A --> B
    A --> C
    A --> D
    C --> B
    D --> B
    C --> H
    C --> G
    D --> F
    E -.-> D
    E -.-> F
    
    style A fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#2196F3,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#FF9800,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#FF9800,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#FFC107,stroke:#333,stroke-width:2px,color:#000
    style F fill:#9C27B0,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#607D8B,stroke:#333,stroke-width:2px,color:#fff
    style H fill:#607D8B,stroke:#333,stroke-width:2px,color:#fff
```

---

# MERMAID DIAGRAM - DATA FLOW

```mermaid
sequenceDiagram
    participant User
    participant Main as main.py
    participant Scraper as scraper.py
    participant CMC as CoinMarketCap
    participant Chrome as WebDriver
    participant DB as database.py
    participant SQL as SQL Server
    
    User->>Main: python main.py
    activate Main
    
    Main->>Main: Setup Logging
    Main->>Scraper: scrape_coinmarketcap()
    activate Scraper
    
    Scraper->>Chrome: Initialize WebDriver
    Chrome-->>Scraper: Driver Ready
    
    Scraper->>CMC: Navigate to URL
    CMC-->>Scraper: HTML Page
    
    Scraper->>Scraper: Scroll & Load Content
    Scraper->>Scraper: Parse with BeautifulSoup
    Scraper-->>Main: crypto_data (List[Dict])
    deactivate Scraper
    
    Main->>DB: save_to_sql_server(crypto_data)
    activate DB
    
    DB->>SQL: Connect
    SQL-->>DB: Connection OK
    
    DB->>SQL: Create Table (if not exists)
    DB->>SQL: INSERT INTO CryptoCurrency
    SQL-->>DB: Success
    
    DB-->>Main: True (Success)
    deactivate DB
    
    Main->>Main: Log Success
    Main-->>User: Execution Complete
    deactivate Main
```

---

# MERMAID DIAGRAM - MODULE DEPENDENCIES

```mermaid
graph LR
    subgraph "Core Application"
        A[main.py]
    end
    
    subgraph "Custom Modules"
        B[scraper.py]
        C[database.py]
        D[config.py]
        E[utils.py]
    end
    
    subgraph "External Libraries"
        F[selenium]
        G[beautifulsoup4]
        H[pyodbc]
        I[pandas]
        J[openpyxl]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> D
    B --> F
    B --> G
    
    C --> D
    C --> H
    
    E --> C
    E --> I
    E --> J
    
    style A fill:#4CAF50,stroke:#333,stroke-width:3px,color:#fff
    style B fill:#FF9800,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#FF9800,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#2196F3,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#FFC107,stroke:#333,stroke-width:2px,color:#000
```

---

# MERMAID DIAGRAM - DATABASE SCHEMA

```mermaid
erDiagram
    CryptoCurrency {
        int id PK "Auto Increment"
        int rank "Crypto Rank"
        nvarchar name "Crypto Name"
        nvarchar price "Current Price"
        nvarchar one_hour_change "1h Change %"
        nvarchar twenty_four_hour_change "24h Change %"
        nvarchar seven_day_change "7d Change %"
        nvarchar market_cap "Market Cap"
        nvarchar volume_24h "24h Volume"
        nvarchar circulating_supply "Supply"
        datetime scraped_at "Timestamp"
    }
```

---

# MERMAID DIAGRAM - EXECUTION FLOW

```mermaid
flowchart TD
    Start([User Runs python main.py]) --> Init[Initialize Logging]
    Init --> Scrape{Start Scraping}
    
    Scrape --> Driver[Initialize Chrome WebDriver]
    Driver --> Navigate[Navigate to CoinMarketCap]
    Navigate --> Wait[Wait for Table Element]
    Wait --> Scroll[Scroll to Load Content]
    Scroll --> Extract[Extract Page Source]
    Extract --> Parse[Parse with BeautifulSoup]
    Parse --> Data{Data Retrieved?}
    
    Data -->|Yes| SaveDB[Save to SQL Server]
    Data -->|No| Error1[Log Error]
    
    SaveDB --> Connect[Connect to SQL Server]
    Connect --> CreateTable[Create Table if Not Exists]
    CreateTable --> Insert[Batch Insert Data]
    Insert --> Commit[Commit Transaction]
    Commit --> Success{Success?}
    
    Success -->|Yes| LogSuccess[Log Success]
    Success -->|No| Error2[Log Error]
    
    Error1 --> End
    Error2 --> End
    LogSuccess --> End([Complete])
    
    style Start fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style End fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style Error1 fill:#f44336,stroke:#333,stroke-width:2px,color:#fff
    style Error2 fill:#f44336,stroke:#333,stroke-width:2px,color:#fff
    style LogSuccess fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
```

---

# SIMPLE TEXT DIAGRAM FOR QUICK REFERENCE

```
PROJECT STRUCTURE:

coinmarketcap-scraper/
│
├── main.py              ← Entry point (orchestrates everything)
│   ├── calls scraper.py
│   └── calls database.py
│
├── scraper.py           ← Web scraping logic
│   ├── Uses: Selenium + BeautifulSoup
│   └── Returns: List[Dict] of crypto data
│
├── database.py          ← SQL Server operations
│   ├── Uses: pyodbc
│   └── Stores data in SQL Server
│
├── config.py            ← Configuration settings
│   ├── DB_CONFIG
│   ├── SCRAPING settings
│   └── CHROME_OPTIONS
│
├── utils.py             ← Optional utilities
│   ├── Export to CSV/Excel
│   └── Data analysis functions
│
└── requirements.txt     ← Python dependencies
```

---

# INSTRUCTIONS FOR DRAW.IO

To create this diagram in Draw.io:

1. **Open Draw.io**: Go to https://app.diagrams.net/

2. **Create Basic Shapes**:
   - Use "Rectangle" for modules
   - Use "Cylinder" for databases
   - Use "Cloud" for external services
   - Use "Arrows" for data flow

3. **Color Coding**:
   - Green: Entry points (main.py)
   - Blue: Configuration (config.py)
   - Orange: Business Logic (scraper.py, database.py)
   - Yellow: Utilities (utils.py)
   - Purple: Databases
   - Grey: External services

4. **Layout Suggestions**:
   - Top-Down flow for execution
   - Left-Right flow for dependencies
   - Grouped boxes for related components

5. **Export Options**:
   - PNG for documentation
   - SVG for web
   - PDF for presentations

---

# ONLINE DIAGRAM TOOLS

You can use these Mermaid diagrams directly in:

1. **Mermaid Live Editor**: https://mermaid.live/
   - Copy any Mermaid code block above
   - Paste and edit
   - Export as PNG/SVG

2. **Draw.io**: https://app.diagrams.net/
   - Import this file or create manually

3. **GitHub**: 
   - Mermaid is natively supported in GitHub markdown

4. **VS Code**:
   - Install "Markdown Preview Mermaid Support" extension
   - View diagrams in markdown preview
