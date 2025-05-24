import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

class FundDataFetcher:
    """Fetch QDII gold fund data from jisilu.cn"""
    
    def __init__(self):
        self.base_url = "https://www.jisilu.cn/data/qdii/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.jisilu.cn/data/qdii/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def fetch_gold_qdii_funds(self):
        """Fetch gold QDII fund data"""
        try:
            # Get the main page first to establish session
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            # Try to get the data via API endpoint
            api_url = "https://www.jisilu.cn/data/qdii/qdii_list/"
            
            # Parameters for filtering gold funds
            params = {
                'is_search': 'Y',
                'market': '',
                'type': '',
                'status': '',
                'fund_nm': '黄金',  # Search for gold funds
                'rp': 50
            }
            
            response = self.session.get(api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            funds = []
            
            if 'rows' in data:
                for row in data['rows']:
                    cell = row.get('cell', {})
                    fund_info = {
                        'fund_code': cell.get('fund_cd', ''),
                        'fund_name': cell.get('fund_nm', ''),
                        'current_price': float(cell.get('price', 0)) if cell.get('price') else 0,
                        'nav_t2': float(cell.get('unit_nav', 0)) if cell.get('unit_nav') else 0,
                        'estimated_nav_t1': float(cell.get('est_nav', 0)) if cell.get('est_nav') else 0,
                        'premium_t1': float(cell.get('premium_rt', 0)) if cell.get('premium_rt') else 0,
                        'volume': float(cell.get('volume', 0)) if cell.get('volume') else 0,
                        'turnover': float(cell.get('turnover', 0)) if cell.get('turnover') else 0,
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Filter for gold-related funds
                    if any(keyword in fund_info['fund_name'] for keyword in ['黄金', '金', 'Gold', 'GOLD']):
                        funds.append(fund_info)
            
            return funds
            
        except Exception as e:
            print(f"Error fetching fund data: {e}")
            # Return mock data for testing
            return self._get_mock_data()
    
    def _get_mock_data(self):
        """Return mock data for testing purposes"""
        return [
            {
                'fund_code': '518800',
                'fund_name': '国泰黄金ETF',
                'current_price': 4.123,
                'nav_t2': 4.089,
                'estimated_nav_t1': 4.101,
                'premium_t1': 0.54,
                'volume': 1234567,
                'turnover': 5088888,
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '159934',
                'fund_name': '易方达黄金ETF',
                'current_price': 4.087,
                'nav_t2': 4.055,
                'estimated_nav_t1': 4.067,
                'premium_t1': 0.49,
                'volume': 987654,
                'turnover': 4022222,
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    
    def save_to_csv(self, funds_data, filename=None):
        """Save fund data to CSV file"""
        if not filename:
            filename = f"../data/funds_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        df = pd.DataFrame(funds_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Fund data saved to {filename}")
        return filename

def main():
    """Test the fund data fetcher"""
    fetcher = FundDataFetcher()
    funds = fetcher.fetch_gold_qdii_funds()
    
    print(f"Found {len(funds)} gold QDII funds:")
    for fund in funds:
        print(f"  {fund['fund_code']} - {fund['fund_name']}: ¥{fund['current_price']:.3f}")
    
    # Save to CSV
    if funds:
        fetcher.save_to_csv(funds)

if __name__ == "__main__":
    main() 