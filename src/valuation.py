import pandas as pd
import numpy as np
from datetime import datetime
import json

class FundValuationAnalyzer:
    """Analyze fund valuation and calculate premium/discount"""
    
    def __init__(self):
        pass
    
    def calculate_estimated_nav(self, nav_t2, gold_return_total):
        """
        Calculate estimated current NAV based on T-2 NAV and gold return
        
        Formula: estimated_nav_now = nav_t2 * (1 + gold_return_total)
        
        Args:
            nav_t2 (float): Net asset value from T-2 (two days ago)
            gold_return_total (float): Total gold return from T-2 to current
            
        Returns:
            float: Estimated current NAV
        """
        if nav_t2 == 0:
            return 0
        
        return nav_t2 * (1 + gold_return_total)
    
    def calculate_premium(self, current_price, estimated_nav):
        """
        Calculate premium rate
        
        Formula: premium = (price_now - estimated_nav_now) / estimated_nav_now
        
        Args:
            current_price (float): Current market price
            estimated_nav (float): Estimated current NAV
            
        Returns:
            float: Premium rate (positive for premium, negative for discount)
        """
        if estimated_nav == 0:
            return 0
        
        return (current_price - estimated_nav) / estimated_nav
    
    def analyze_single_fund(self, fund_data, gold_data):
        """
        Analyze a single fund's valuation
        
        Args:
            fund_data (dict): Fund information including nav_t2, current_price, etc.
            gold_data (dict): Gold price and return data
            
        Returns:
            dict: Analysis results
        """
        # Extract key values
        nav_t2 = fund_data.get('nav_t2', 0)
        current_price = fund_data.get('current_price', 0)
        gold_return_total = gold_data.get('gold_return_total', 0)
        
        # Calculate estimated NAV
        estimated_nav = self.calculate_estimated_nav(nav_t2, gold_return_total)
        
        # Calculate current premium
        current_premium = self.calculate_premium(current_price, estimated_nav)
        
        # Get historical premium for comparison
        premium_t1 = fund_data.get('premium_t1', 0) / 100  # Convert percentage to decimal
        
        # Calculate premium change
        premium_change = current_premium - premium_t1
        
        # Determine arbitrage opportunity
        arbitrage_signal = self._get_arbitrage_signal(current_premium)
        
        return {
            'fund_code': fund_data.get('fund_code', ''),
            'fund_name': fund_data.get('fund_name', ''),
            'nav_t2': nav_t2,
            'estimated_nav_current': estimated_nav,
            'current_price': current_price,
            'premium_t1': premium_t1,
            'premium_current': current_premium,
            'premium_change': premium_change,
            'gold_return_total': gold_return_total,
            'arbitrage_signal': arbitrage_signal,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def analyze_multiple_funds(self, funds_data, gold_data):
        """
        Analyze multiple funds
        
        Args:
            funds_data (list): List of fund data dictionaries
            gold_data (dict): Gold price and return data
            
        Returns:
            list: List of analysis results
        """
        results = []
        
        for fund_data in funds_data:
            try:
                analysis = self.analyze_single_fund(fund_data, gold_data)
                results.append(analysis)
            except Exception as e:
                print(f"Error analyzing fund {fund_data.get('fund_code', 'Unknown')}: {e}")
                continue
        
        # Sort by premium rate (most discount first)
        results.sort(key=lambda x: x['premium_current'])
        
        return results
    
    def _get_arbitrage_signal(self, premium_rate):
        """
        Determine arbitrage signal based on premium rate
        
        Args:
            premium_rate (float): Current premium rate
            
        Returns:
            str: Signal ('BUY', 'SELL', 'HOLD')
        """
        if premium_rate < -0.01:  # More than 1% discount
            return 'BUY'
        elif premium_rate > 0.01:  # More than 1% premium
            return 'SELL'
        else:
            return 'HOLD'
    
    def get_summary_stats(self, analysis_results):
        """
        Get summary statistics across all funds
        
        Args:
            analysis_results (list): List of analysis results
            
        Returns:
            dict: Summary statistics
        """
        if not analysis_results:
            return {}
        
        premiums = [result['premium_current'] for result in analysis_results]
        
        return {
            'total_funds': len(analysis_results),
            'avg_premium': np.mean(premiums),
            'median_premium': np.median(premiums),
            'min_premium': np.min(premiums),
            'max_premium': np.max(premiums),
            'std_premium': np.std(premiums),
            'funds_at_discount': sum(1 for p in premiums if p < 0),
            'funds_at_premium': sum(1 for p in premiums if p > 0),
            'buy_signals': sum(1 for result in analysis_results if result['arbitrage_signal'] == 'BUY'),
            'sell_signals': sum(1 for result in analysis_results if result['arbitrage_signal'] == 'SELL'),
        }
    
    def save_analysis_to_csv(self, analysis_results, filename=None):
        """Save analysis results to CSV"""
        if not filename:
            filename = f"../data/analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df = pd.DataFrame(analysis_results)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Analysis results saved to {filename}")
        return filename

def main():
    """Test the valuation analyzer"""
    analyzer = FundValuationAnalyzer()
    
    # Mock data for testing
    fund_data = {
        'fund_code': '518800',
        'fund_name': '国泰黄金ETF',
        'current_price': 4.123,
        'nav_t2': 4.089,
        'premium_t1': 0.54
    }
    
    gold_data = {
        'gold_return_total': 0.0247  # 2.47% return
    }
    
    result = analyzer.analyze_single_fund(fund_data, gold_data)
    
    print("Fund Analysis Result:")
    print(f"Fund: {result['fund_name']} ({result['fund_code']})")
    print(f"T-2 NAV: ¥{result['nav_t2']:.3f}")
    print(f"Estimated Current NAV: ¥{result['estimated_nav_current']:.3f}")
    print(f"Current Price: ¥{result['current_price']:.3f}")
    print(f"Current Premium: {result['premium_current']:.4f} ({result['premium_current']*100:.2f}%)")
    print(f"T-1 Premium: {result['premium_t1']:.4f} ({result['premium_t1']*100:.2f}%)")
    print(f"Premium Change: {result['premium_change']:.4f} ({result['premium_change']*100:.2f}%)")
    print(f"Arbitrage Signal: {result['arbitrage_signal']}")

if __name__ == "__main__":
    main() 