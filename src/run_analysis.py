import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from datetime import datetime
import os
import sys

# Add the src directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_fund import FundDataFetcher
from fetch_gold import GoldDataFetcher  
from valuation import FundValuationAnalyzer

class QDIIGoldAnalyzer:
    """Main analyzer class that orchestrates the entire analysis workflow"""
    
    def __init__(self):
        self.fund_fetcher = FundDataFetcher()
        self.gold_fetcher = GoldDataFetcher()
        self.analyzer = FundValuationAnalyzer()
        
        # Ensure output directories exist
        os.makedirs('../data', exist_ok=True)
        os.makedirs('../charts', exist_ok=True)
    
    def run_complete_analysis(self):
        """Run the complete analysis workflow"""
        print("🏅 QDII黄金基金实时估值与溢价分析系统")
        print("=" * 50)
        
        # Step 1: Fetch gold price data
        print("📈 Fetching gold price data...")
        gold_data = self.gold_fetcher.fetch_all_data()
        
        # Step 2: Fetch fund data
        print("⛏ Fetching fund data from 集思录...")
        funds_data = self.fund_fetcher.fetch_gold_qdii_funds()
        
        if not funds_data:
            print("❌ No fund data available")
            return None
        
        # Step 3: Analyze all funds
        print("🧠 Analyzing fund valuations...")
        analysis_results = self.analyzer.analyze_multiple_funds(funds_data, gold_data)
        
        # Step 4: Display results
        self.display_results(analysis_results, gold_data)
        
        # Step 5: Create visualizations
        print("📊 Creating visualizations...")
        self.create_visualizations(analysis_results, gold_data)
        
        # Step 6: Save data
        self.save_results(analysis_results, gold_data)
        
        return analysis_results
    
    def display_results(self, analysis_results, gold_data):
        """Display analysis results in a formatted table"""
        print("\n" + "=" * 80)
        print(f"📊 分析结果 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("=" * 80)
        
        # Display gold market info
        gold_prices = gold_data['gold_prices']
        print(f"🥇 黄金价格信息:")
        print(f"   T-2: ${gold_prices['t2']['price']:.2f} ({gold_prices['t2']['date']})")
        print(f"   T-1: ${gold_prices['t1']['price']:.2f} ({gold_prices['t1']['date']})")
        print(f"   当前: ${gold_prices['current']['price']:.2f} ({gold_prices['current']['date']})")
        print(f"   总涨幅: {gold_data['gold_return_total']:.4f} ({gold_data['gold_return_total']*100:.2f}%)")
        print(f"💱 汇率 (USD/CNY): {gold_data['exchange_rate']:.4f}")
        
        # Display fund analysis
        print(f"\n📋 基金分析结果:")
        print("-" * 80)
        print(f"{'基金代码':<8} {'基金名称':<12} {'现价':<8} {'估值':<8} {'溢价率':<8} {'信号':<6}")
        print("-" * 80)
        
        for result in analysis_results:
            premium_pct = result['premium_current'] * 100
            signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
            signal_display = f"{signal_emoji.get(result['arbitrage_signal'], '⚪')} {result['arbitrage_signal']}"
            
            print(f"{result['fund_code']:<8} {result['fund_name'][:10]:<12} "
                  f"{result['current_price']:<8.3f} {result['estimated_nav_current']:<8.3f} "
                  f"{premium_pct:<7.2f}% {signal_display:<10}")
        
        # Display summary statistics
        stats = self.analyzer.get_summary_stats(analysis_results)
        if stats:
            print(f"\n📈 统计摘要:")
            print(f"   总基金数: {stats['total_funds']}")
            print(f"   平均溢价率: {stats['avg_premium']*100:.2f}%")
            print(f"   溢价基金数: {stats['funds_at_premium']}")
            print(f"   折价基金数: {stats['funds_at_discount']}")
            print(f"   买入信号: {stats['buy_signals']}")
            print(f"   卖出信号: {stats['sell_signals']}")
    
    def create_visualizations(self, analysis_results, gold_data):
        """Create comprehensive Plotly visualizations"""
        if not analysis_results:
            return
        
        # Create main dashboard with subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '基金溢价率分布',
                '估值 vs 市价对比', 
                '黄金价格趋势',
                '套利信号分布'
            ),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Prepare data
        fund_names = [r['fund_name'][:8] for r in analysis_results]
        premiums = [r['premium_current'] * 100 for r in analysis_results]
        current_prices = [r['current_price'] for r in analysis_results]
        estimated_navs = [r['estimated_nav_current'] for r in analysis_results]
        signals = [r['arbitrage_signal'] for r in analysis_results]
        
        # Plot 1: Premium rate distribution
        colors = ['red' if p > 1 else 'green' if p < -1 else 'orange' for p in premiums]
        fig.add_trace(
            go.Bar(x=fund_names, y=premiums, name='溢价率(%)', marker_color=colors),
            row=1, col=1
        )
        
        # Plot 2: Price vs NAV comparison
        fig.add_trace(
            go.Scatter(x=estimated_navs, y=current_prices, mode='markers+text',
                      text=fund_names, textposition="top center",
                      marker=dict(size=12, color=premiums, colorscale='RdYlGn_r',
                                showscale=True, colorbar=dict(title="溢价率(%)")),
                      name='基金价格'),
            row=1, col=2
        )
        
        # Add diagonal line for reference (price = nav)
        min_val = min(min(estimated_navs), min(current_prices))
        max_val = max(max(estimated_navs), max(current_prices))
        fig.add_trace(
            go.Scatter(x=[min_val, max_val], y=[min_val, max_val],
                      mode='lines', line=dict(dash='dash', color='gray'),
                      name='价格=净值线'),
            row=1, col=2
        )
        
        # Plot 3: Gold price trend
        gold_prices = gold_data['gold_prices']
        gold_dates = [gold_prices['t2']['date'], gold_prices['t1']['date'], gold_prices['current']['date']]
        gold_price_values = [gold_prices['t2']['price'], gold_prices['t1']['price'], gold_prices['current']['price']]
        
        fig.add_trace(
            go.Scatter(x=gold_dates, y=gold_price_values, mode='lines+markers',
                      line=dict(color='gold', width=3),
                      marker=dict(size=10), name='黄金价格'),
            row=2, col=1
        )
        
        # Plot 4: Signal distribution
        signal_counts = pd.Series(signals).value_counts()
        signal_colors = {'BUY': 'green', 'SELL': 'red', 'HOLD': 'orange'}
        colors_list = [signal_colors.get(signal, 'gray') for signal in signal_counts.index]
        
        fig.add_trace(
            go.Pie(labels=signal_counts.index, values=signal_counts.values,
                  marker_colors=colors_list, name="信号分布"),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"🏅 QDII黄金基金实时分析仪表板<br><sub>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</sub>",
                x=0.5,
                font=dict(size=20)
            ),
            height=800,
            showlegend=True,
            template="plotly_white"
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="基金", row=1, col=1)
        fig.update_yaxes(title_text="溢价率(%)", row=1, col=1)
        fig.update_xaxes(title_text="估算净值", row=1, col=2)
        fig.update_yaxes(title_text="市场价格", row=1, col=2)
        fig.update_xaxes(title_text="日期", row=2, col=1)
        fig.update_yaxes(title_text="价格(USD)", row=2, col=1)
        
        # Save the dashboard
        dashboard_file = f"../charts/qdii_gold_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(dashboard_file)
        print(f"📊 Dashboard saved to: {dashboard_file}")
        
        # Create additional detailed charts
        self.create_detailed_charts(analysis_results, gold_data)
        
        # Show the dashboard
        fig.show()
    
    def create_detailed_charts(self, analysis_results, gold_data):
        """Create additional detailed charts"""
        
        # 1. Premium comparison chart
        fig_premium = go.Figure()
        
        fund_names = [r['fund_name'] for r in analysis_results]
        premium_current = [r['premium_current'] * 100 for r in analysis_results]
        premium_t1 = [r['premium_t1'] * 100 for r in analysis_results]
        premium_change = [r['premium_change'] * 100 for r in analysis_results]
        
        fig_premium.add_trace(go.Bar(
            name='T-1溢价率', x=fund_names, y=premium_t1,
            marker_color='lightblue'
        ))
        fig_premium.add_trace(go.Bar(
            name='当前溢价率', x=fund_names, y=premium_current,
            marker_color='darkblue'
        ))
        
        fig_premium.update_layout(
            title='溢价率对比分析',
            xaxis_title='基金',
            yaxis_title='溢价率(%)',
            barmode='group',
            template="plotly_white"
        )
        
        premium_file = f"../charts/premium_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig_premium.write_html(premium_file)
        print(f"📊 Premium comparison chart saved to: {premium_file}")
        
        # 2. Fund performance heatmap
        df_results = pd.DataFrame(analysis_results)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=[premium_current],
            x=fund_names,
            y=['溢价率'],
            colorscale='RdYlGn_r',
            text=[[f'{p:.2f}%' for p in premium_current]],
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="溢价率(%)")
        ))
        
        fig_heatmap.update_layout(
            title='基金溢价率热力图',
            template="plotly_white",
            height=200
        )
        
        heatmap_file = f"../charts/premium_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig_heatmap.write_html(heatmap_file)
        print(f"📊 Premium heatmap saved to: {heatmap_file}")
    
    def save_results(self, analysis_results, gold_data):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save analysis results
        analysis_file = self.analyzer.save_analysis_to_csv(analysis_results, 
                                                          f"../data/analysis_{timestamp}.csv")
        
        # Save gold data
        gold_df = pd.DataFrame([{
            'date': gold_data['gold_prices']['current']['date'],
            'gold_price_current': gold_data['gold_prices']['current']['price'],
            'gold_price_t1': gold_data['gold_prices']['t1']['price'],
            'gold_price_t2': gold_data['gold_prices']['t2']['price'],
            'gold_return_total': gold_data['gold_return_total'],
            'exchange_rate': gold_data['exchange_rate'],
            'update_time': gold_data['update_time']
        }])
        
        gold_file = f"../data/gold_data_{timestamp}.csv"
        gold_df.to_csv(gold_file, index=False, encoding='utf-8')
        print(f"💾 Gold data saved to: {gold_file}")
        
        print(f"💾 Analysis complete! Results saved to data/ and charts/ directories")

def main():
    """Main function to run the analysis"""
    try:
        analyzer = QDIIGoldAnalyzer()
        results = analyzer.run_complete_analysis()
        
        if results:
            print("\n✅ Analysis completed successfully!")
            print("📁 Check the data/ directory for CSV files")
            print("📊 Check the charts/ directory for HTML visualizations")
        else:
            print("\n❌ Analysis failed!")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 