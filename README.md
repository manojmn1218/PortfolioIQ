# CP-006 PortfolioIQ: Equity Portfolio and P&L Analytics System

**PortfolioIQ** is a terminal-based Equity Portfolio & Profit/Loss (P&L) Analytics System developed in Python. Designed for retail investors and financial analysts, the application tracks stock trades, maintains an accurate weighted-average buy price across transactions, and separates realized gains (from closed positions) from unrealized gains (on open positions). It provides real-time portfolio valuation against current market prices, sector allocation breakdown, automated risk alerts for drawdowns exceeding 10%, and exportable formatted portfolio statements.

---

## 👥 Team
| Name | USN | Department |
| :--- | :--- | :--- |
| **Manoj M N** | 1AT24AI055 | AIML |
| **Ananya R** | 1AT24AI006 | AIML |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher.
- Built using **pure Python standard library** (`datetime`, `os`) — **no external dependencies or pip installations required**.

### How to Run
```bash
python main.py
```

---

## 📌 Features

### Core Features
1. **Trade Execution & Validation (BUY / SELL)**
   - Records buy and sell trades with stock symbol, quantity, price, and execution date.
   - Automatically recalibrates the **weighted-average cost basis** upon additional buys.
   - Validates sell transactions against active holdings and strictly **rejects invalid oversells / short selling**.
2. **Current Holdings & Cost-Basis Tracking**
   - Displays all active stock positions with symbol, sector, held quantity, average buy price, total invested amount, and Last Traded Price (LTP).
3. **Daily Market Price Updates & Mark-to-Market P&L**
   - Allows users to update today's market price for each holding.
   - Computes individual stock P&L (absolute and percentage) along with total portfolio market value and gain/loss.
4. **Realised vs. Unrealised P&L Accounting**
   - Separates **Realised Profit/Loss** (locked in cash gains/losses from completed sales) from **Unrealised Profit/Loss** (paper gains/losses on open positions).
   - Computes total net portfolio performance.
5. **Sector Allocation Analysis**
   - Groups equity holdings by industry sector (e.g., IT, Banking, Energy, Auto, Pharma, FMCG).
   - Calculates percentage distribution and displays visual terminal bar indicators.
6. **Trade History Ledger**
   - Full audit trail logging every executed trade with unique sequence IDs (`TRD1001`, `TRD1002`, ...), timestamp, trade type, quantity, execution price, and realized profit/loss.

### Stretch Features
7. **🚨 Risk Management & Drawdown Alerts (>10% Drop)**
   - Automatically monitors all open holdings against today's prices.
   - Flags an immediate warning when any stock drops more than **10%** below its weighted-average purchase price, detailing percentage drawdown and unrealised loss.
8. **📄 Export Portfolio Statement to File**
   - Generates a timestamped, formatted text report (`portfolio_statement_YYYYMMDD_HHMMSS.txt`) summarizing capital invested, current market value, P&L breakdown, stock-by-stock metrics, and active risk alerts.

---


## 🖥️ Terminal Interface & Menu Options

```text
========================================================================
   CP-006 PORTFOLIOIQ: EQUITY PORTFOLIO & P&L ANALYTICS SYSTEM
========================================================================
    1. Record Buy / Sell Trade     |  5. Sector Allocation (%)
    2. View Holdings & Avg Price   |  6. Drawdown Alerts (>10% Drop)
    3. Update Today's Prices & P&L |  7. Export Statement to File
    4. Realised vs Unrealised P&L  |  8. View Trade History Ledger
                                   |  0. Exit Application
========================================================================
```

---

## 📊 Sample Execution Walkthrough

### 1. Viewing Holdings & Weighted Average Buy Price (Option 2)
```text
==============================================================================
  2. CURRENT HOLDINGS & WEIGHTED AVERAGE BUY PRICE (5 Stocks)
==============================================================================
  Symbol       Sector        Qty   Avg Buy (Rs.)   Invested (Rs.)     LTP (Rs.)
  --------------------------------------------------------------------------
  TCS          IT             15         3700.00         55500.00       3920.00
  HDFCBANK     Banking        30         1650.00         49500.00       1720.00
  RELIANCE     Energy         15         2900.00         43500.00       2980.00
  TATAMOTORS   Auto           25          950.00         23750.00        820.00
  SUNPHARMA    Pharma         12         1800.00         21600.00       1860.00
  --------------------------------------------------------------------------
  TOTAL COST BASIS                             Rs.    193850.00
```

### 2. Realised vs. Unrealised Profit & Loss Accounting (Option 4)
```text
==============================================================================
  4. REALISED vs UNREALISED PROFIT & LOSS ACCOUNTING
==============================================================================
  Symbol       Qty Held     Realised P&L     Unrealised P&L          Net P&L
  --------------------------------------------------------------------------
  HDFCBANK           30            +0.00           +2100.00         +2100.00
  RELIANCE           15            +0.00           +1200.00         +1200.00
  SUNPHARMA          12            +0.00            +720.00          +720.00
  TATAMOTORS         25            +0.00           -3250.00         -3250.00
  TCS                15         +1250.00           +3300.00         +4550.00
  --------------------------------------------------------------------------
  Total Realised P&L (Closed Sales)   : +1250.00 Rs.
  Total Unrealised P&L (Open Holdings): +4070.00 Rs.
  Net Portfolio P&L                   : +5320.00 Rs.
```

### 3. Sector Allocation Distribution (Option 5)
```text
==========================================================================
  5. PORTFOLIO ALLOCATION BY SECTOR
==========================================================================
  Sector             Market Value (Rs.)   Allocation %   Distribution
  ----------------------------------------------------------------------
  IT                           58800.00         29.52%   ########
  Banking                      51600.00         25.91%   ######
  Energy                       44700.00         22.44%   ######
  Pharma                       22320.00         11.21%   ###
  Auto                         20500.00         10.29%   ###
  ----------------------------------------------------------------------
  TOTAL PORTFOLIO             199170.00        100.00%
```

### 4. Drawdown Risk Alerts (Option 6)
```text
==========================================================================
  6. STRETCH FEATURE: RISK ALERTS (>10% BELOW AVG BUY PRICE)
==========================================================================
  [ALERT] 1 holding(s) breached the -10% drawdown threshold:

  Symbol       Avg Buy (Rs.)   Today (Rs.)     Drop % Unrealised Loss
  ----------------------------------------------------------------------
  TATAMOTORS          950.00        820.00    -13.68%  Rs. -3250.00
```

---

## 📂 Project Architecture

```
PortfolioIQ/
│
├── main.py        # Complete application source code (CLI, Business Logic, State)
└── README.md      # Comprehensive system documentation & user guide
```

---

## 🛡️ Robust Validation & Error Handling
- **Input Guardrails**: Rejects negative quantities, non-numeric values, invalid stock tickers, and out-of-range dates.
- **Oversell Prevention**: Automatically blocks attempts to sell more shares than currently held.
- **Safe Defaults**: Seeds realistic demo data upon launch to allow immediate testing and exploration without manual configuration.
