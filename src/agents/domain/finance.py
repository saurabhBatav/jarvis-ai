"""Finance Agent - Personal finance tracking and market analysis"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict
import yfinance as yf
import duckdb
import os


class FinanceTools:
    """Free financial tools for Jarvis"""
    
    @staticmethod
    def get_stock_price(symbol: str) -> Dict:
        """Get current stock price (Free: Yahoo Finance)"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                "symbol": symbol.upper(),
                "price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "change": info.get("regularMarketChange", "N/A"),
                "change_percent": info.get("regularMarketChangePercent", "N/A"),
                "volume": info.get("volume", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "company": info.get("shortName", symbol)
            }
        except Exception as e:
            return {"error": str(e), "symbol": symbol}

    @staticmethod
    def get_stock_history(symbol: str, period: str = "1mo") -> Dict:
        """Get stock historical data"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            if hist.empty:
                return {"error": "No data available"}
            
            return {
                "symbol": symbol.upper(),
                "period": period,
                "latest_close": float(hist['Close'].iloc[-1]),
                "high": float(hist['High'].max()),
                "low": float(hist['Low'].min()),
                "volume": int(hist['Volume'].sum())
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_crypto_price(symbol: str) -> Dict:
        """Get cryptocurrency price (Yahoo Finance)"""
        try:
            # Add USD suffix for Yahoo Finance
            crypto = yf.Ticker(f"{symbol}-USD")
            info = crypto.info
            return {
                "symbol": symbol.upper(),
                "price": info.get("currentPrice", "N/A"),
                "change": info.get("regularMarketChange", "N/A"),
                "market_cap": info.get("marketCap", "N/A")
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def search_stocks(query: str) -> List[Dict]:
        """Search for stocks by name"""
        try:
            # Use Yahoo Finance to search
            tickers = yf.Tickers(query)
            results = []
            for symbol in list(tickers.tickers.keys())[:5]:
                try:
                    info = tickers.tickers[symbol].info
                    results.append({
                        "symbol": symbol,
                        "name": info.get("shortName", symbol),
                        "type": info.get("quoteType", "UNKNOWN")
                    })
                except:
                    continue
            return results
        except Exception as e:
            return [{"error": str(e)}]


class PortfolioDatabase:
    """Local portfolio tracking with DuckDB (Free)"""
    
    def __init__(self, db_path: str = "./memory/portfolio.duckdb"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY,
                symbol VARCHAR,
                quantity DOUBLE,
                avg_price DOUBLE,
                purchase_date DATE,
                notes VARCHAR
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                symbol VARCHAR,
                type VARCHAR,
                quantity DOUBLE,
                price DOUBLE,
                date DATE
            )
        """)
        conn.close()
    
    def add_holding(self, symbol: str, quantity: float, avg_price: float, notes: str = ""):
        conn = duckdb.connect(self.db_path)
        conn.execute("""
            INSERT INTO holdings (symbol, quantity, avg_price, purchase_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (symbol.upper(), quantity, avg_price, datetime.now().date(), notes))
        conn.close()
    
    def get_holdings(self) -> List[Dict]:
        conn = duckdb.connect(self.db_path)
        result = conn.execute("SELECT * FROM holdings").fetchall()
        conn.close()
        return [
            {"id": r[0], "symbol": r[1], "quantity": r[2], "avg_price": r[3], 
             "purchase_date": str(r[4]), "notes": r[5]}
            for r in result
        ]
    
    def get_portfolio_value(self) -> float:
        holdings = self.get_holdings()
        total = 0
        for h in holdings:
            price_data = FinanceTools.get_stock_price(h["symbol"])
            if "price" in price_data and price_data["price"]:
                total += price_data["price"] * h["quantity"]
        return total


class FinanceAgent:
    """
    Personal Finance Agent with free tools:
    - Yahoo Finance for stock/crypto prices
    - DuckDB for local portfolio tracking
    - No API keys required
    """
    
    def __init__(self, portfolio_db_path: str = "./memory/portfolio.duckdb"):
        self.tools = FinanceTools()
        self.portfolio = PortfolioDatabase(portfolio_db_path)
        self._instructions = """You are Jarvis Finance Agent, a personal financial advisor.
Your role is to help users track investments, analyze stocks, and manage portfolio.
Always be accurate with numbers and provide clear explanations.
Use simple language since users may not be finance experts.
Focus on helping users make informed decisions."""
    
    def get_instructions(self, user_context: str = "") -> str:
        base = self._instructions
        if user_context:
            portfolio = self.portfolio.get_holdings()
            holdings_info = f"\nUser's current holdings: {portfolio}" if portfolio else ""
            return base + f"\n\nUser context: {user_context}{holdings_info}"
        return base
    
    def check_portfolio(self) -> str:
        """Check current portfolio status"""
        holdings = self.portfolio.get_holdings()
        if not holdings:
            return "Your portfolio is empty. Add holdings to track your investments."
        
        total_value = 0
        lines = ["📊 Your Portfolio:\n"]
        
        for h in holdings:
            price_data = self.tools.get_stock_price(h["symbol"])
            current_price = price_data.get("price", 0)
            if current_price:
                value = current_price * h["quantity"]
                total_value += value
                cost = h["avg_price"] * h["quantity"]
                gain_loss = value - cost
                gain_loss_pct = (gain_loss / cost) * 100 if cost > 0 else 0
                
                lines.append(f"{h['symbol']}: {h['quantity']} shares @ ${h['avg_price']:.2f}")
                lines.append(f"  Current: ${current_price:.2f} | Value: ${value:.2f} | P/L: ${gain_loss:.2f} ({gain_loss_pct:+.1f}%)")
        
        lines.append(f"\nTotal Value: ${total_value:.2f}")
        return "\n".join(lines)
    
    def add_holding(self, symbol: str, quantity: float, price: float, notes: str = "") -> str:
        self.portfolio.add_holding(symbol, quantity, price, notes)
        return f"✅ Added {quantity} shares of {symbol.upper()} at ${price:.2f}"
    
    def get_stock_info(self, symbol: str) -> str:
        data = self.tools.get_stock_price(symbol)
        if "error" in data:
            return f"Error: {data['error']}"
        
        lines = [f"📈 {data['company']} ({data['symbol']})"]
        lines.append(f"Price: ${data['price']}")
        if data['change']:
            lines.append(f"Change: ${data['change']:.2f} ({data['change_percent']:+.2f}%)")
        if data.get('volume'):
            lines.append(f"Volume: {data['volume']:,}")
        if data.get('market_cap'):
            lines.append(f"Market Cap: ${data['market_cap']/1e9:.2f}B")
        
        return "\n".join(lines)
    
    def get_crypto(self, symbol: str) -> str:
        data = self.tools.get_crypto_price(symbol)
        if "error" in data:
            return f"Error: {data['error']}"
        
        return f"₿ {data['symbol']}: ${data['price']} ({data['change']:+.2f}%)"
    
    def analyze(self, query: str) -> str:
        """Answer finance questions"""
        query_lower = query.lower()
        
        if "portfolio" in query_lower or "holdings" in query_lower:
            return self.check_portfolio()
        
        if "add" in query_lower and "holding" in querylower:
            return "Use add_holding(symbol, quantity, price) to add holdings"
        
        # Try to extract stock symbol
        words = query.split()
        for word in words:
            if word.isupper() and len(word) <= 5:
                return self.get_stock_info(word)
        
        return "I can help with stock prices, crypto, and portfolio tracking. What would you like to know?"