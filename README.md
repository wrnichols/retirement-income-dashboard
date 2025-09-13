# Retirement Income Calculator Dashboard

A comprehensive Streamlit dashboard for calculating and analyzing retirement income needs for financial advisory clients.

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

2. Run the dashboard:
```bash
streamlit run retirement_dashboard.py
```

## Usage

1. Enter client demographics and retirement timeline in the sidebar
2. Input Social Security benefit estimates at different claiming ages
3. Add pension, other income sources, and LTC insurance coverage
4. Click "Calculate Retirement Needs" to generate analysis
5. Review charts and detailed summary for client presentation

## Key Outputs

- **Assets Needed at Retirement**: Amount required with 90% success probability
- **Assets Needed Today**: Present value of retirement goal
- **Required Growth Rate**: Annual return needed to reach target
- **Income Projections**: Year-by-year breakdown of needs vs. sources
- **Success Probability**: Monte Carlo analysis across asset levels

## Assumptions

- Post-retirement return: 5% nominal (10% volatility)
- Inflation: 2.9% (2025-2026), 2.3% thereafter
- LTC cost inflation: 5% annually with 15% AI reduction by 2030
- Georgia tax: 5.49% flat rate with $65K exclusion at age 65+
- Federal taxes: 2025 brackets with progressive rates