# 🏅 QDII黄金基金实时估值与溢价分析系统

本项目通过集思录与国际黄金数据源，结合黄金价格涨跌与基金T-2净值，实时估算黄金QDII基金当前应有估值，并与市场成交价格进行比较，判断是否存在溢价/折价套利机会。

---

## 🔧 功能概述

- ⛏ 从[集思录](https://www.jisilu.cn/data/qdii/#qdiiea)自动获取黄金QDII基金的：
  - T-2净值
  - T-1估值
  - T-1溢价率
  - 实时交易价格
- 📈 从 `Yahoo Finance` 等来源抓取伦敦金价格（T-2、T-1、当前）
- 💱 获取汇率（美元兑人民币）
- 🧠 使用黄金回报与净值关系，估算实时净值
- 🧮 自动计算当前实时溢价率
- 📊 支持 CLI 表格输出和 **Plotly** 图表可视化

---

## 📁 项目结构

```
qdii-gold-arbitrage/
├── data/                    # 数据文件（缓存、CSV）
├── charts/                  # 图表输出文件
├── src/
│   ├── fetch_fund.py       # 获取基金数据（集思录）
│   ├── fetch_gold.py       # 获取黄金数据
│   ├── valuation.py        # 净值与溢价估算逻辑
│   └── run_analysis.py     # 主程序入口
├── notebooks/
│   └── qdii_gold_analysis.ipynb  # Jupyter分析笔记本
├── README.md
└── requirements.txt
```

---

## ⚡ 快速开始

### 1. 环境设置

```bash
# 克隆项目
git clone <repository_url>
cd etf_delta

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行分析

```bash
# 命令行运行完整分析
cd src
python run_analysis.py
```

### 3. 查看结果

运行后将生成：
- 📊 **交互式HTML仪表板** (`charts/qdii_gold_dashboard_*.html`)
- 📈 **详细图表** (`charts/premium_comparison_*.html`, `charts/premium_heatmap_*.html`)
- 💾 **数据文件** (`data/analysis_*.csv`, `data/gold_data_*.csv`)

### 4. Jupyter笔记本

```bash
# 启动Jupyter
jupyter notebook notebooks/qdii_gold_analysis.ipynb
```

---

## 🧪 实时估值计算逻辑

```python
# Gold total return (T-2 → current)
gold_return_total = (gold_now - gold_t2) / gold_t2

# Fund real-time estimated value = T-2 NAV × (1 + total gold return)
estimated_nav_now = nav_t2 * (1 + gold_return_total)

# Premium rate = (current market price - estimated NAV) / estimated NAV
premium = (price_now - estimated_nav_now) / estimated_nav_now
```

---

## 📊 可视化功能

### 🎯 主仪表板
- **基金溢价率分布柱状图**
- **估值vs市价散点图**
- **黄金价格趋势线图**
- **交易信号分布饼图**

### 📈 详细图表
- **溢价率对比分析**
- **基金表现热力图**
- **历史溢价率变化**

### 🚦 交易信号
- 🟢 **BUY**: 溢价率 < -1% (折价超过1%)
- 🔴 **SELL**: 溢价率 > 1% (溢价超过1%)
- 🟡 **HOLD**: -1% ≤ 溢价率 ≤ 1%

---

## 🔍 使用示例

### 命令行输出示例：
```
🏅 QDII黄金基金实时估值与溢价分析系统
==================================================
📈 Fetching gold price data...
⛏ Fetching fund data from 集思录...
🧠 Analyzing fund valuations...

================================================================================
📊 分析结果 (2024-01-15 14:30:25)
================================================================================
🥇 黄金价格信息:
   T-2: $2020.50 (2024-01-13)
   T-1: $2022.30 (2024-01-14)
   当前: $2025.00 (2024-01-15)
   总涨幅: 0.0222 (2.22%)
💱 汇率 (USD/CNY): 7.1850

📋 基金分析结果:
--------------------------------------------------------------------------------
基金代码    基金名称        现价      估值      溢价率    信号
--------------------------------------------------------------------------------
518800   国泰黄金ETF     4.123    4.180    -1.36%   🟢 BUY
159934   易方达黄金ETF   4.087    4.144    -1.38%   🟢 BUY
```

---

## 📦 依赖说明

- `requests`: HTTP请求库，用于数据获取
- `beautifulsoup4`: HTML解析，处理网页数据
- `pandas`: 数据处理和分析
- `plotly`: 交互式可视化图表
- `yfinance`: Yahoo Finance数据接口
- `numpy`: 数值计算

---

## ⚠️ 注意事项

1. **数据来源**: 项目依赖外部数据源，可能因网络或API限制影响数据获取
2. **投资建议**: 本工具仅供分析参考，不构成投资建议
3. **实时性**: 数据更新频率取决于数据源的更新频率
4. **准确性**: 估值计算基于模型假设，实际情况可能有差异

---

## 🚀 功能扩展

### 计划中的功能：
- [ ] 历史数据回测
- [ ] 更多技术指标
- [ ] 邮件/微信通知
- [ ] Web界面部署
- [ ] 更多基金类型支持

---

## 📞 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。

---

## �� 许可证

MIT License
