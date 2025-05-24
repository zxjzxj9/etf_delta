import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

class GoldDataFetcher:
    """Fetch gold price and exchange rate data"""
    
    def __init__(self):
        self.gold_symbol = "GC=F"  # Gold futures
        self.usd_cny_symbol = "USDCNY=X"  # USD to CNY exchange rate
        
    def fetch_gold_prices(self, days_back=5):
        """
        Fetch gold prices for the last few days
        Returns dict with dates and prices
        """
        try:
            # Get gold data
            gold_ticker = yf.Ticker(self.gold_symbol)
            
            # Get data for the last week to ensure we have T-2, T-1, and current
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            hist_data = gold_ticker.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                print("No gold price data available, using mock data")
                return self._get_mock_gold_data()
            
            # Get the latest prices
            prices = {}
            dates = hist_data.index.tolist()
            close_prices = hist_data['Close'].tolist()
            
            # Get current (latest available)
            prices['current'] = {
                'price': close_prices[-1],
                'date': dates[-1].strftime('%Y-%m-%d')
            }
            
            # Get T-1 (previous day)
            if len(close_prices) >= 2:
                prices['t1'] = {
                    'price': close_prices[-2],
                    'date': dates[-2].strftime('%Y-%m-%d')
                }
            else:
                prices['t1'] = prices['current']
            
            # Get T-2 (two days ago)
            if len(close_prices) >= 3:
                prices['t2'] = {
                    'price': close_prices[-3],
                    'date': dates[-3].strftime('%Y-%m-%d')
                }
            else:
                prices['t2'] = prices['t1']
            
            return prices
            
        except Exception as e:
            print(f"Error fetching gold prices: {e}")
            return self._get_mock_gold_data()
    
    def fetch_exchange_rate(self):
        """Fetch USD to CNY exchange rate"""
        try:
            # Try multiple sources for exchange rate
            
            # Method 1: Yahoo Finance
            try:
                usd_cny = yf.Ticker(self.usd_cny_symbol)
                hist = usd_cny.history(period="1d")
                if not hist.empty:
                    return hist['Close'].iloc[-1]
            except:
                pass
            
            # Method 2: Exchange rate API (free tier)
            try:
                response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return data['rates'].get('CNY', 7.2)
            except:
                pass
            
            # Method 3: Fallback to approximate rate
            print("Using fallback exchange rate")
            return 7.2  # Approximate USD to CNY rate
            
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return 7.2
    
    def _get_mock_gold_data(self):
        """Return mock gold price data for testing"""
        base_price = 2020.0  # USD per ounce
        return {
            'current': {
                'price': base_price + 5.0,
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            't1': {
                'price': base_price + 2.0,
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            },
            't2': {
                'price': base_price,
                'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            }
        }
    
    def get_gold_return(self, gold_prices):
        """Calculate gold return from T-2 to current"""
        try:
            gold_t2 = gold_prices['t2']['price']
            gold_current = gold_prices['current']['price']
            
            if gold_t2 == 0:
                return 0
            
            return (gold_current - gold_t2) / gold_t2
            
        except Exception as e:
            print(f"Error calculating gold return: {e}")
            return 0
    
    def fetch_all_data(self):
        """Fetch all required data: gold prices and exchange rate"""
        gold_prices = self.fetch_gold_prices()
        exchange_rate = self.fetch_exchange_rate()
        gold_return = self.get_gold_return(gold_prices)
        
        return {
            'gold_prices': gold_prices,
            'exchange_rate': exchange_rate,
            'gold_return_total': gold_return,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """Test the gold data fetcher"""
    fetcher = GoldDataFetcher()
    data = fetcher.fetch_all_data()
    
    print("Gold Price Data:")
    for period, info in data['gold_prices'].items():
        print(f"  {period.upper()}: ${info['price']:.2f} ({info['date']})")
    
    print(f"\nUSD/CNY Exchange Rate: {data['exchange_rate']:.4f}")
    print(f"Gold Return (T-2 to Current): {data['gold_return_total']:.4f} ({data['gold_return_total']*100:.2f}%)")

if __name__ == "__main__":
    main() 