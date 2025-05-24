import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
import numpy as np

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
        
        # Expanded keywords for better gold fund detection
        self.gold_keywords = [
            # Chinese keywords
            '黄金', '贵金属', '金矿', '金ETF', '黄金ETF',
            # English keywords
            'Gold', 'GOLD', 'Precious', 'Metal', 'GLD', 'IAU', 'Mining',
            # Fund code patterns that typically indicate gold funds
            'Au', 'AU'
        ]
        
    def fetch_gold_qdii_funds(self):
        """Fetch gold QDII fund data with comprehensive search"""
        all_funds = []
        
        # Search with multiple keywords to catch more gold funds
        search_terms = ['黄金', 'Gold', 'GOLD', '贵金属', 'GLD', 'IAU', '上海金', 'AU', '金ETF', '黄金易']
        
        for search_term in search_terms:
            funds = self._search_funds_by_keyword(search_term)
            if funds:
                all_funds.extend(funds)
        
        # Remove duplicates based on fund code
        unique_funds = {}
        for fund in all_funds:
            fund_code = fund.get('fund_code', '')
            if fund_code and fund_code not in unique_funds:
                unique_funds[fund_code] = fund
        
        result_funds = list(unique_funds.values())
        
        # Apply additional filtering for gold-related funds
        filtered_funds = []
        for fund in result_funds:
            if self._is_gold_related_fund(fund):
                filtered_funds.append(fund)
        
        if not filtered_funds:
            print("⚠️ No funds found from API, using mock data for testing")
            return self._get_mock_data()
        
        print(f"✅ Found {len(filtered_funds)} gold-related funds")
        return filtered_funds
        
    def _search_funds_by_keyword(self, keyword):
        """Search for funds using a specific keyword"""
        try:
            # Get the main page first to establish session
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            # Try to get the data via API endpoint
            api_url = "https://www.jisilu.cn/data/qdii/qdii_list/C/"
            
            # Parameters for filtering funds
            params = {
                'is_search': 'Y',
                'market': '',
                'type': '',
                'status': '',
                'fund_nm': keyword,
                'rp': 100  # Increased to get more results
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
                    funds.append(fund_info)
            
            print(f"🔍 Search '{keyword}': found {len(funds)} funds")
            return funds
            
        except Exception as e:
            print(f"Error searching for keyword '{keyword}': {e}")
            return []
    
    def _is_gold_related_fund(self, fund_info):
        """Enhanced check if a fund is gold-related"""
        fund_name = fund_info.get('fund_name', '').upper()
        fund_code = fund_info.get('fund_code', '').upper()
        
        # Primary gold keywords (high confidence)
        primary_keywords = ['黄金', 'GOLD', 'GLD', 'IAU', '金ETF', '黄金ETF']
        for keyword in primary_keywords:
            if keyword.upper() in fund_name or keyword.upper() in fund_code:
                return True
        
        # Secondary gold keywords (medium confidence)
        secondary_keywords = ['贵金属', 'PRECIOUS', 'METAL', '金矿', 'MINING', 'AU']
        secondary_count = 0
        for keyword in secondary_keywords:
            if keyword.upper() in fund_name or keyword.upper() in fund_code:
                secondary_count += 1
        
        # If multiple secondary keywords match, likely gold-related
        if secondary_count >= 2:
            return True
        
        # Check for common gold fund code patterns (expanded list)
        gold_patterns = [
            # Major Gold ETFs
            '518800',  # 国泰黄金ETF
            '159934',  # 易方达黄金ETF  
            '518880',  # 华安黄金易ETF
            '159937',  # 华夏黄金ETF
            '518660',  # 工银瑞信黄金ETF
            '159812',  # 天弘上海金ETF
            '164699',  # 富国上海金ETF
            # Gold ETF Feeder Funds (联接基金)
            '000216',  # 华安黄金易ETF联接A
            '000217',  # 华安黄金易ETF联接C
            '004253',  # 易方达黄金ETF联接A
            '004254',  # 易方达黄金ETF联接C
            '000929',  # 国泰黄金ETF联接A
            '002084',  # 国泰黄金ETF联接C
            '001518',  # 华夏黄金ETF联接A
            '001519',  # 华夏黄金ETF联接C
            # Additional Gold-related funds
            '040801',  # 华安黄金易ETF联接
            '002216',  # 工银黄金ETF联接A
            '002217',  # 工银黄金ETF联接C
            '159739',  # 天弘黄金ETF联接A
            '159740',  # 天弘黄金ETF联接C
        ]
        if fund_code in gold_patterns:
            return True
        
        # Additional checks for fund names that might contain gold references
        gold_related_terms = ['金', '贵', 'SPDR', 'GOLD', 'BULLION']
        for term in gold_related_terms:
            if term in fund_name and ('ETF' in fund_name or 'QDII' in fund_name):
                return True
        
        return False
    
    def get_all_qdii_funds(self):
        """Get all QDII funds without filtering (for comprehensive analysis)"""
        try:
            # Get the main page first to establish session
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            # Try to get all QDII data via API endpoint
            api_url = "https://www.jisilu.cn/data/qdii/qdii_list/C/"
            
            # Parameters to get all funds
            params = {
                'is_search': 'N',
                'market': '',
                'type': '',
                'status': '',
                'fund_nm': '',
                'rp': 200  # Get more funds
            }
            
            response = self.session.get(api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            all_funds = []
            
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
                    all_funds.append(fund_info)
            
            # Filter for gold-related funds
            gold_funds = []
            for fund in all_funds:
                if self._is_gold_related_fund(fund):
                    gold_funds.append(fund)
            
            print(f"📊 Analyzed {len(all_funds)} total QDII funds, found {len(gold_funds)} gold-related funds")
            return gold_funds if gold_funds else self._get_mock_data()
            
        except Exception as e:
            print(f"Error fetching all QDII funds: {e}")
            return self._get_mock_data()

    def _get_mock_data(self):
        """Return comprehensive mock data for testing with all major gold ETFs"""
        base_price = 4.0 + np.random.normal(0, 0.2)  # Base around 4.0 with variation
        
        funds = [
            # Main Gold ETFs
            {
                'fund_code': '518800',
                'fund_name': '国泰黄金ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,  # Will be calculated
                'estimated_nav_t1': 0,  # Will be calculated  
                'premium_t1': round(np.random.normal(0.5, 0.2), 2),
                'volume': int(np.random.uniform(800000, 1500000)),
                'turnover': int(np.random.uniform(3000000, 6000000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '159934',
                'fund_name': '易方达黄金ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.4, 0.2), 2),
                'volume': int(np.random.uniform(700000, 1300000)),
                'turnover': int(np.random.uniform(2500000, 5500000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '518880',
                'fund_name': '华安黄金易ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.45, 0.2), 2),
                'volume': int(np.random.uniform(600000, 1200000)),
                'turnover': int(np.random.uniform(2200000, 5000000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '159937',
                'fund_name': '华夏黄金ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.48, 0.2), 2),
                'volume': int(np.random.uniform(550000, 1100000)),
                'turnover': int(np.random.uniform(2000000, 4500000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '518660',
                'fund_name': '工银瑞信黄金ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.42, 0.2), 2),
                'volume': int(np.random.uniform(400000, 900000)),
                'turnover': int(np.random.uniform(1500000, 3500000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '159812',
                'fund_name': '天弘上海金ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.46, 0.2), 2),
                'volume': int(np.random.uniform(350000, 800000)),
                'turnover': int(np.random.uniform(1200000, 3000000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '164699',
                'fund_name': '富国上海金ETF',
                'current_price': round(base_price + np.random.normal(0, 0.1), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.44, 0.2), 2),
                'volume': int(np.random.uniform(300000, 700000)),
                'turnover': int(np.random.uniform(1000000, 2800000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            # Gold ETF Feeder Funds (lower prices)
            {
                'fund_code': '000216',
                'fund_name': '华安黄金易ETF联接A',
                'current_price': round(1.2 + np.random.normal(0, 0.05), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.35, 0.15), 2),
                'volume': int(np.random.uniform(200000, 500000)),
                'turnover': int(np.random.uniform(800000, 2000000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '004253',
                'fund_name': '易方达黄金ETF联接A',
                'current_price': round(1.15 + np.random.normal(0, 0.05), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.32, 0.15), 2),
                'volume': int(np.random.uniform(180000, 450000)),
                'turnover': int(np.random.uniform(700000, 1800000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'fund_code': '000929',
                'fund_name': '国泰黄金ETF联接A',
                'current_price': round(1.18 + np.random.normal(0, 0.05), 3),
                'nav_t2': 0,
                'estimated_nav_t1': 0,
                'premium_t1': round(np.random.normal(0.38, 0.15), 2),
                'volume': int(np.random.uniform(160000, 400000)),
                'turnover': int(np.random.uniform(600000, 1600000)),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        # Calculate nav_t2 and estimated_nav_t1 based on current_price and premium
        for fund in funds:
            current = fund['current_price']
            premium = fund['premium_t1'] / 100  # Convert percentage to decimal
            
            # Estimate NAV based on current price and premium
            estimated_nav = current / (1 + premium)
            fund['estimated_nav_t1'] = round(estimated_nav, 3)
            
            # T-2 NAV with slight variation
            nav_variation = np.random.normal(0, 0.01)  # ±1% variation
            fund['nav_t2'] = round(estimated_nav * (1 + nav_variation), 3)
        
        return funds
    
    def save_to_csv(self, funds_data, filename=None):
        """Save fund data to CSV file"""
        if not filename:
            filename = f"../data/funds_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        df = pd.DataFrame(funds_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"💾 Fund data saved to {filename}")
        return filename

def main():
    """Test the fund data fetcher"""
    fetcher = FundDataFetcher()
    
    print("🔍 Testing enhanced gold fund search...")
    funds = fetcher.fetch_gold_qdii_funds()
    
    print(f"\n📈 Found {len(funds)} gold QDII funds:")
    for fund in funds:
        print(f"  {fund['fund_code']} - {fund['fund_name']}: ¥{fund['current_price']:.3f}")
    
    # Test comprehensive search
    print(f"\n🔍 Testing comprehensive QDII fund analysis...")
    all_gold_funds = fetcher.get_all_qdii_funds()
    print(f"📊 Comprehensive search found {len(all_gold_funds)} gold-related funds")
    
    # Save to CSV
    if funds:
        fetcher.save_to_csv(funds)

if __name__ == "__main__":
    main() 
