from datetime import datetime
import os

# =====================================================================
# 1. CONSTANTS & SECTOR DIRECTORY
# =====================================================================
VALID_TRADE_TYPES = ["BUY", "SELL"]
DRAWDOWN_ALERT_THRESHOLD_PCT = 10.0

DEFAULT_SECTORS = {
    "TCS": "IT",
    "INFY": "IT",
    "WIPRO": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "RELIANCE": "Energy",
    "ONGC": "Energy",
    "TATAMOTORS": "Auto",
    "MARUTI": "Auto",
    "SUNPHARMA": "Pharma",
    "CIPLA": "Pharma",
    "ITC": "FMCG",
    "HINDUNILVR": "FMCG",
}

# =====================================================================
# 2. IN-MEMORY PORTFOLIO STATE (Pure Python Dicts & Lists)
# =====================================================================
# trades: list of {"trade_id", "symbol", "side", "qty", "price", "date", "realised_pnl"}
# holdings: dict keyed by symbol -> {"symbol", "sector", "qty", "avg_buy_price", "realised_pnl", "current_price"}
trades = []
holdings = {}
next_trade_seq = 1001

# =====================================================================
# 3. HELPER & VALIDATION FUNCTIONS
# =====================================================================
def today_date():
    return datetime.now().strftime("%Y-%m-%d")

def generate_trade_id():
    global next_trade_seq
    tid = f"TRD{next_trade_seq}"
    next_trade_seq += 1
    return tid

def input_symbol(prompt_msg="Enter Stock Symbol (e.g., TCS, INFY, HDFCBANK): "):
    while True:
        sym = input(prompt_msg).strip().upper()
        if 1 <= len(sym) <= 15 and sym.isalnum():
            return sym
        print("  [!] Invalid symbol. Use 1-15 alphanumeric characters (e.g., TCS).")

def input_trade_side():
    while True:
        side = input("Enter Trade Type (BUY / SELL): ").strip().upper()
        if side in VALID_TRADE_TYPES:
            return side
        print("  [!] Invalid trade type. Allowed: BUY, SELL")

def input_positive_int(prompt_msg, min_val=1, max_val=1000000):
    while True:
        raw = input(prompt_msg).strip()
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  [!] Quantity must be between {min_val} and {max_val}.")
        except ValueError:
            print("  [!] Invalid quantity. Please enter a whole number.")

def input_positive_float(prompt_msg, min_val=0.01, max_val=10000000.0):
    while True:
        raw = input(prompt_msg).strip()
        try:
            val = round(float(raw), 2)
            if min_val <= val <= max_val:
                return val
            print(f"  [!] Value must be between {min_val:.2f} and {max_val:.2f}.")
        except ValueError:
            print("  [!] Invalid number. Please enter a valid numeric value.")

def input_date(prompt_msg=None):
    default_dt = today_date()
    if prompt_msg is None:
        prompt_msg = f"Enter Trade Date (YYYY-MM-DD, Enter for {default_dt}): "
    while True:
        raw = input(prompt_msg).strip()
        if not raw:
            return default_dt
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("  [!] Invalid date format. Please use YYYY-MM-DD (e.g., 2026-11-16).")

def resolve_sector(symbol):
    if symbol in holdings:
        return holdings[symbol]["sector"]
    if symbol in DEFAULT_SECTORS:
        return DEFAULT_SECTORS[symbol]
    sector = input(f"Enter Sector for {symbol} (e.g., IT, Banking, Energy, Auto, Pharma): ").strip()
    return sector if sector else "Other"

def apply_trade_to_state(symbol, side, qty, price, trade_date, sector=None):
    """Apply BUY or SELL trade to holdings using weighted-average cost & realised P&L accounting."""
    if symbol not in holdings:
        holdings[symbol] = {
            "symbol": symbol,
            "sector": sector or DEFAULT_SECTORS.get(symbol, "Other"),
            "qty": 0,
            "avg_buy_price": 0.0,
            "realised_pnl": 0.0,
            "current_price": round(price, 2),
        }

    h = holdings[symbol]
    realised = 0.0

    if side == "BUY":
        total_cost = (h["qty"] * h["avg_buy_price"]) + (qty * price)
        new_qty = h["qty"] + qty
        h["avg_buy_price"] = round(total_cost / new_qty, 2)
        h["qty"] = new_qty
        h["current_price"] = round(price, 2)
    else:
        if qty > h["qty"]:
            return None, f"Insufficient shares! Holding {h['qty']} of {symbol}, cannot sell {qty}."
        realised = round((price - h["avg_buy_price"]) * qty, 2)
        h["realised_pnl"] = round(h["realised_pnl"] + realised, 2)
        h["qty"] -= qty
        h["current_price"] = round(price, 2)
        if h["qty"] == 0:
            h["avg_buy_price"] = 0.0

    trade = {
        "trade_id": generate_trade_id(),
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "price": round(price, 2),
        "date": trade_date,
        "realised_pnl": realised,
    }
    trades.append(trade)
    return trade, None

def get_active_holdings():
    return [h for h in holdings.values() if h["qty"] > 0]

def compute_portfolio_summary():
    active = get_active_holdings()
    total_invested = sum(h["qty"] * h["avg_buy_price"] for h in active)
    total_market_val = sum(h["qty"] * h["current_price"] for h in active)
    total_unrealised = sum((h["current_price"] - h["avg_buy_price"]) * h["qty"] for h in active)
    total_realised = sum(h["realised_pnl"] for h in holdings.values())
    return {
        "active": active,
        "total_invested": round(total_invested, 2),
        "total_market_val": round(total_market_val, 2),
        "total_unrealised": round(total_unrealised, 2),
        "total_realised": round(total_realised, 2),
        "net_pnl": round(total_realised + total_unrealised, 2),
    }

# =====================================================================
# 4. CORE FEATURE 1: RECORD BUY / SELL TRADES
# =====================================================================
def record_trade():
    print("\n" + "=" * 72)
    print("  1. RECORD BUY / SELL TRADE")
    print("=" * 72)

    symbol = input_symbol()
    side = input_trade_side()

    if side == "SELL":
        held_qty = holdings[symbol]["qty"] if symbol in holdings else 0
        if held_qty <= 0:
            print(f"\n  [REJECTED] You do not hold any shares of {symbol} to sell.")
            return
        print(f"  [INFO] Current Holding: {held_qty} shares of {symbol} @ Avg Rs. {holdings[symbol]['avg_buy_price']:.2f}")

    qty = input_positive_int("Enter Quantity (shares): ")
    price = input_positive_float("Enter Trade Price per Share (Rs.): ")
    trade_date = input_date()
    sector = resolve_sector(symbol) if side == "BUY" else None

    trade, err = apply_trade_to_state(symbol, side, qty, price, trade_date, sector)
    if err:
        print(f"\n  [REJECTED] {err}")
        return

    h = holdings[symbol]
    print(f"\n  [SUCCESS] Recorded {side} {qty} {symbol} @ Rs. {price:.2f} on {trade_date} (Ref: {trade['trade_id']}).")
    if side == "BUY":
        print(f"  Updated Holding: {h['qty']} shares | New Weighted Avg Price: Rs. {h['avg_buy_price']:.2f}")
    else:
        sign = "+" if trade["realised_pnl"] >= 0 else ""
        print(f"  Realised P&L from Sale: {sign}Rs. {trade['realised_pnl']:.2f} | Remaining Qty: {h['qty']} shares")

# =====================================================================
# 5. CORE FEATURE 2: SHOW CURRENT HOLDINGS & AVERAGE BUY PRICE
# =====================================================================
def show_holdings():
    active = get_active_holdings()
    print("\n" + "=" * 78)
    print(f"  2. CURRENT HOLDINGS & WEIGHTED AVERAGE BUY PRICE ({len(active)} Stocks)")
    print("=" * 78)
    if not active:
        print("  No active holdings in portfolio.")
        return

    print(f"  {'Symbol':<12} {'Sector':<10} {'Qty':>6} {'Avg Buy (Rs.)':>15} {'Invested (Rs.)':>16} {'LTP (Rs.)':>13}")
    print("  " + "-" * 74)
    total_inv = 0.0
    for h in active:
        inv = h["qty"] * h["avg_buy_price"]
        total_inv += inv
        print(
            f"  {h['symbol']:<12} {h['sector']:<10} {h['qty']:>6} "
            f"{h['avg_buy_price']:>15.2f} {inv:>16.2f} {h['current_price']:>13.2f}"
        )
    print("  " + "-" * 74)
    print(f"  {'TOTAL COST BASIS':<44} Rs. {total_inv:>12.2f}")

# =====================================================================
# 6. CORE FEATURE 3: ENTER TODAY'S PRICES & SHOW P&L PER STOCK / TOTAL
# =====================================================================
def update_todays_prices_and_pnl():
    active = get_active_holdings()
    print("\n" + "=" * 78)
    print("  3. UPDATE TODAY'S PRICES & PORTFOLIO P&L")
    print("=" * 78)
    if not active:
        print("  No active holdings to price.")
        return

    print("  Enter today's market price for each stock (press Enter to keep current LTP):\n")
    for h in active:
        while True:
            raw = input(f"  {h['symbol']:<12} (Avg: Rs. {h['avg_buy_price']:.2f}, Current LTP: Rs. {h['current_price']:.2f}) -> New Price: ").strip()
            if not raw:
                break
            try:
                val = round(float(raw), 2)
                if val > 0:
                    h["current_price"] = val
                    break
                print("    [!] Price must be greater than 0.")
            except ValueError:
                print("    [!] Invalid price. Enter a valid number or press Enter.")

    summary = compute_portfolio_summary()
    print("\n  " + "-" * 76)
    print(f"  {'Symbol':<11} {'Qty':>5} {'Avg Buy':>10} {'Today':>10} {'Curr Val':>12} {'P&L (Rs.)':>12} {'P&L %':>8}")
    print("  " + "-" * 76)
    for h in active:
        curr_val = h["qty"] * h["current_price"]
        pnl = (h["current_price"] - h["avg_buy_price"]) * h["qty"]
        pnl_pct = ((h["current_price"] - h["avg_buy_price"]) / h["avg_buy_price"]) * 100 if h["avg_buy_price"] > 0 else 0.0
        sign = "+" if pnl >= 0 else ""
        print(
            f"  {h['symbol']:<11} {h['qty']:>5} {h['avg_buy_price']:>10.2f} "
            f"{h['current_price']:>10.2f} {curr_val:>12.2f} {sign}{pnl:>11.2f} {sign}{pnl_pct:>6.2f}%"
        )
    print("  " + "-" * 76)
    tot_pnl = summary["total_unrealised"]
    tot_pct = (tot_pnl / summary["total_invested"] * 100) if summary["total_invested"] > 0 else 0.0
    sign = "+" if tot_pnl >= 0 else ""
    print(f"  Total Invested : Rs. {summary['total_invested']:.2f}")
    print(f"  Current Value  : Rs. {summary['total_market_val']:.2f}")
    print(f"  Total Open P&L : {sign}Rs. {tot_pnl:.2f} ({sign}{tot_pct:.2f}%)")

# =====================================================================
# 7. CORE FEATURE 4: REALISED VS UNREALISED P&L BREAKDOWN
# =====================================================================
def show_realised_vs_unrealised():
    print("\n" + "=" * 78)
    print("  4. REALISED vs UNREALISED PROFIT & LOSS ACCOUNTING")
    print("=" * 78)
    if not holdings:
        print("  No trades recorded yet.")
        return

    print(f"  {'Symbol':<12} {'Qty Held':>8} {'Realised P&L':>16} {'Unrealised P&L':>18} {'Net P&L':>16}")
    print("  " + "-" * 74)
    for sym in sorted(holdings.keys()):
        h = holdings[sym]
        unrealised = (h["current_price"] - h["avg_buy_price"]) * h["qty"] if h["qty"] > 0 else 0.0
        net = h["realised_pnl"] + unrealised
        print(
            f"  {sym:<12} {h['qty']:>8} "
            f"{h['realised_pnl']:>+16.2f} {unrealised:>+18.2f} {net:>+16.2f}"
        )

    summary = compute_portfolio_summary()
    print("  " + "-" * 74)
    print(f"  Total Realised P&L (Closed Sales)   : {summary['total_realised']:+.2f} Rs.")
    print(f"  Total Unrealised P&L (Open Holdings): {summary['total_unrealised']:+.2f} Rs.")
    print(f"  Net Portfolio P&L                   : {summary['net_pnl']:+.2f} Rs.")

# =====================================================================
# 8. CORE FEATURE 5: SECTOR ALLOCATION (% OF PORTFOLIO)
# =====================================================================
def show_sector_allocation():
    active = get_active_holdings()
    print("\n" + "=" * 74)
    print("  5. PORTFOLIO ALLOCATION BY SECTOR")
    print("=" * 74)
    if not active:
        print("  No active holdings to analyze.")
        return

    sector_values = {}
    total_val = 0.0
    for h in active:
        val = h["qty"] * h["current_price"]
        sector_values[h["sector"]] = sector_values.get(h["sector"], 0.0) + val
        total_val += val

    print(f"  {'Sector':<16} {'Market Value (Rs.)':>20} {'Allocation %':>14}   {'Distribution'}")
    print("  " + "-" * 70)
    for sec, val in sorted(sector_values.items(), key=lambda x: x[1], reverse=True):
        pct = (val / total_val) * 100.0 if total_val > 0 else 0.0
        bars = "#" * max(1, int(round(pct / 4)))
        print(f"  {sec:<16} {val:>20.2f} {pct:>13.2f}%   {bars}")
    print("  " + "-" * 70)
    print(f"  {'TOTAL PORTFOLIO':<16} {total_val:>20.2f} {'100.00%':>14}")

# =====================================================================
# 9. STRETCH FEATURE 1: DRAWDOWN ALERTS (>10% BELOW AVG BUY PRICE)
# =====================================================================
def get_drawdown_alerts():
    alerts = []
    for h in get_active_holdings():
        if h["avg_buy_price"] <= 0:
            continue
        drop_pct = ((h["avg_buy_price"] - h["current_price"]) / h["avg_buy_price"]) * 100.0
        if drop_pct > DRAWDOWN_ALERT_THRESHOLD_PCT:
            alerts.append((h, round(drop_pct, 2)))
    return alerts

def show_drawdown_alerts():
    print("\n" + "=" * 74)
    print(f"  6. STRETCH FEATURE: RISK ALERTS (>{DRAWDOWN_ALERT_THRESHOLD_PCT:.0f}% BELOW AVG BUY PRICE)")
    print("=" * 74)
    alerts = get_drawdown_alerts()
    if not alerts:
        print(f"  [OK] No holdings are more than {DRAWDOWN_ALERT_THRESHOLD_PCT:.0f}% below their average buy price.")
        return

    print(f"  [ALERT] {len(alerts)} holding(s) breached the -{DRAWDOWN_ALERT_THRESHOLD_PCT:.0f}% drawdown threshold:\n")
    print(f"  {'Symbol':<12} {'Avg Buy (Rs.)':>14} {'Today (Rs.)':>13} {'Drop %':>10} {'Unrealised Loss'}")
    print("  " + "-" * 70)
    for h, drop_pct in alerts:
        loss = (h["current_price"] - h["avg_buy_price"]) * h["qty"]
        print(f"  {h['symbol']:<12} {h['avg_buy_price']:>14.2f} {h['current_price']:>13.2f} -{drop_pct:>8.2f}%  Rs. {loss:.2f}")

# =====================================================================
# 10. STRETCH FEATURE 2: EXPORT PORTFOLIO STATEMENT TO FILE
# =====================================================================
def export_statement():
    print("\n" + "=" * 74)
    print("  7. STRETCH FEATURE: EXPORT PORTFOLIO STATEMENT TO FILE")
    print("=" * 74)

    summary = compute_portfolio_summary()
    alerts = get_drawdown_alerts()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"portfolio_statement_{ts}.txt"
    filename = input(f"  Enter output filename (Enter for {default_filename}): ").strip() or default_filename

    lines = [
        "=" * 74,
        "  CP-006 PORTFOLIOIQ: EQUITY PORTFOLIO & P&L STATEMENT",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 74,
        f"  Total Invested Capital : Rs. {summary['total_invested']:.2f}",
        f"  Current Market Value   : Rs. {summary['total_market_val']:.2f}",
        f"  Total Realised P&L     : {summary['total_realised']:+.2f} Rs.",
        f"  Total Unrealised P&L   : {summary['total_unrealised']:+.2f} Rs.",
        f"  Net Portfolio P&L      : {summary['net_pnl']:+.2f} Rs.",
        "",
        "  HOLDINGS BREAKDOWN:",
        f"  {'Symbol':<12} {'Sector':<10} {'Qty':>5} {'Avg Buy':>11} {'LTP':>11} {'Unrealised':>14}",
        "  " + "-" * 68,
    ]
    for h in summary["active"]:
        unr = (h["current_price"] - h["avg_buy_price"]) * h["qty"]
        lines.append(
            f"  {h['symbol']:<12} {h['sector']:<10} {h['qty']:>5} "
            f"{h['avg_buy_price']:>11.2f} {h['current_price']:>11.2f} {unr:>+14.2f}"
        )

    lines.append("")
    if alerts:
        lines.append(f"  DRAWDOWN ALERTS (>{DRAWDOWN_ALERT_THRESHOLD_PCT:.0f}% BELOW AVG PRICE):")
        for h, drop_pct in alerts:
            lines.append(f"  [!] {h['symbol']}: Avg Rs. {h['avg_buy_price']:.2f} -> Today Rs. {h['current_price']:.2f} (-{drop_pct:.2f}%)")
    else:
        lines.append("  DRAWDOWN ALERTS: None")
    lines.append("=" * 74)

    out_path = os.path.abspath(filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\n  [SUCCESS] Portfolio statement exported to: {out_path}")

def show_trade_history():
    print("\n" + "=" * 74)
    print(f"  8. TRADE HISTORY LEDGER ({len(trades)} Trades)")
    print("=" * 74)
    if not trades:
        print("  No trades recorded yet.")
        return

    print(f"  {'Trade ID':<10} {'Date':<12} {'Side':<6} {'Symbol':<12} {'Qty':>5} {'Price (Rs.)':>12} {'Realised P&L'}")
    print("  " + "-" * 70)
    for t in trades:
        rpnl = f"{t['realised_pnl']:+.2f}" if t["side"] == "SELL" else "-"
        print(f"  {t['trade_id']:<10} {t['date']:<12} {t['side']:<6} {t['symbol']:<12} {t['qty']:>5} {t['price']:>12.2f} {rpnl:>12}")

# =====================================================================
# 11. SEED DEMO DATA & MAIN MENU LOOP
# =====================================================================
def seed_demo_data():
    demo_trades = [
        ("TCS",        "BUY",  10, 3600.00, "2026-10-05", "IT"),
        ("TCS",        "BUY",  10, 3800.00, "2026-10-18", "IT"),
        ("TCS",        "SELL",  5, 3950.00, "2026-11-02", "IT"),
        ("HDFCBANK",   "BUY",  20, 1600.00, "2026-10-10", "Banking"),
        ("HDFCBANK",   "BUY",  10, 1750.00, "2026-10-25", "Banking"),
        ("RELIANCE",   "BUY",  15, 2900.00, "2026-10-12", "Energy"),
        ("TATAMOTORS", "BUY",  25,  950.00, "2026-10-20", "Auto"),
        ("SUNPHARMA",  "BUY",  12, 1800.00, "2026-11-01", "Pharma"),
    ]
    for sym, side, qty, price, dt, sec in demo_trades:
        apply_trade_to_state(sym, side, qty, price, dt, sec)

    # Set realistic today's market prices (TATAMOTORS >10% down to demonstrate Alert!)
    demo_ltp = {
        "TCS": 3920.00,
        "HDFCBANK": 1720.00,
        "RELIANCE": 2980.00,
        "TATAMOTORS": 820.00,   # -13.68% below Rs. 950 avg -> triggers >10% alert
        "SUNPHARMA": 1860.00,
    }
    for sym, ltp in demo_ltp.items():
        if sym in holdings:
            holdings[sym]["current_price"] = ltp

def print_menu():
    print("\n" + "=" * 72)
    print("   CP-006 PORTFOLIOIQ: EQUITY PORTFOLIO & P&L ANALYTICS SYSTEM")
    print("=" * 72)
    print("    1. Record Buy / Sell Trade     |  5. Sector Allocation (%)")
    print("    2. View Holdings & Avg Price   |  6. Drawdown Alerts (>10% Drop)")
    print("    3. Update Today's Prices & P&L |  7. Export Statement to File")
    print("    4. Realised vs Unrealised P&L  |  8. View Trade History Ledger")
    print("                                   |  0. Exit Application")
    print("=" * 72)

def main():
    seed_demo_data()
    while True:
        print_menu()
        choice = input("Select an option (0-8): ").strip()
        if choice == "1":
            record_trade()
        elif choice == "2":
            show_holdings()
        elif choice == "3":
            update_todays_prices_and_pnl()
        elif choice == "4":
            show_realised_vs_unrealised()
        elif choice == "5":
            show_sector_allocation()
        elif choice == "6":
            show_drawdown_alerts()
        elif choice == "7":
            export_statement()
        elif choice == "8":
            show_trade_history()
        elif choice == "0":
            print("\nThank you for using PortfolioIQ (CP-006). Exiting...")
            break
        else:
            print("  [!] Invalid option. Please enter 0-8.")

if __name__ == "__main__":
    main()
