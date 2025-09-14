# Retirement Income Calculator Dashboards

Two comprehensive Streamlit dashboards for financial advisory clients:

## 🏦 Dashboard 1: Retirement Income Calculator
Calculates minimum assets needed to meet desired spending goals.

## 💸 Dashboard 2: Retirement Spending Calculator
Determines sustainable spending levels based on current assets.

## Features

- **Monte Carlo Simulation**: 90% success probability analysis with 1,000+ simulations
- **Tax-Aware Calculations**: Federal and Georgia state tax considerations
- **Social Security Optimization**: Analysis of claiming strategies (ages 62, FRA, 70)
- **Long-Term Care Planning**: AI-adjusted cost projections with insurance coverage
- **Interactive Visualizations**: Income sources, success probability charts
- **Client-Friendly Interface**: Intuitive sidebar inputs with real-time calculations

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the dashboards:

**Income Calculator (Asset Requirements):**
```bash
streamlit run streamlit_app.py
```

**Spending Calculator (Sustainable Spending):**
```bash
python run_spending_dashboard.py
# OR
streamlit run retirement_spending_dashboard.py --server.port 8502
```

## Usage

### Dashboard 1: Income Calculator
1. Enter client demographics and desired monthly income
2. Input Social Security benefit estimates at different claiming ages
3. Add pension, other income sources, and LTC insurance coverage
4. Click "Calculate Retirement Needs" to see required assets
5. Review charts showing income sources vs. needs

### Dashboard 2: Spending Calculator
1. Enter current assets and investment risk tolerance
2. Input demographics and retirement timeline
3. Add Social Security and other income projections
4. Click "Calculate Sustainable Spending" to see spending levels
5. Review Monte Carlo analysis with three confidence levels (80%, 90%, 95%)

## Key Outputs

### Dashboard 1: Income Calculator
- **Assets Needed at Retirement**: Amount required with 90% success probability
- **Assets Needed Today**: Present value of retirement goal
- **Required Growth Rate**: Annual return needed to reach target
- **Income Projections**: Year-by-year breakdown of needs vs. sources

### Dashboard 2: Spending Calculator
- **Sustainable Spending Levels**: Monthly amounts at 80%, 90%, and 95% success rates
- **Assets at Retirement**: Projected portfolio value at retirement
- **Success Probability Analysis**: Monte Carlo results across spending levels
- **Income Source Breakdown**: Social Security, pension, and other income over time

## Assumptions

- Post-retirement return: 5% nominal (10% volatility)
- Inflation: 2.9% (2025-2026), 2.3% thereafter
- LTC cost inflation: 5% annually with 15% AI reduction by 2030
- Georgia tax: 5.49% flat rate with $65K exclusion at age 65+
- Federal taxes: 2025 brackets with progressive rates
