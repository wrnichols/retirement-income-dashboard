import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm

# Configuration constants
POST_RET_RETURN_MEAN = 0.05
POST_RET_RETURN_SD = 0.10
INFLATION_SHORT = 0.029
INFLATION_LONG = 0.023
SAFE_WITHDRAWAL_RATE = 0.04
TAX_RATE_EFFECTIVE = 0.15
GA_RESIDENT = True
GA_EXCLUSION_65PLUS = 65000
FED_BRACKETS_SINGLE = [0, 11600, 47150, 100525, 191950, 243725, 609350]
FED_RATES = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
GA_TAX_RATE = 0.0549
LTC_INFLATION = 0.05
LTC_BASE_COST = 100000
AI_LTC_REDUCTION = 0.15
NUM_SIM = 1000
SUCCESS_PROB = 0.90

def calculate_federal_tax(income, filing='single'):
    """Progressive federal tax on taxable income."""
    brackets = FED_BRACKETS_SINGLE if filing == 'single' else [b * 2 for b in FED_BRACKETS_SINGLE]
    tax = 0
    prev = 0
    for i, rate in enumerate(FED_RATES):
        if i == len(FED_RATES) - 1:
            tax += max(0, income - prev) * rate
        else:
            bracket = min(income, brackets[i+1])
            tax += max(0, bracket - prev) * rate
            prev = brackets[i+1]
            if income <= brackets[i+1]:
                break
    return tax

def ss_taxable(provisional_income):
    """SS taxable portion (simplified: thresholds for single)."""
    if provisional_income < 25000:
        return 0
    elif provisional_income < 34000:
        return 0.50
    else:
        return 0.85

def retirement_calculator(
    current_age, years_to_ret, years_to_ss, monthly_income, legacy_desired=0,
    ss_min=0, ss_fra=0, ss_max=0, fra_age=67, inflation_rate=INFLATION_LONG,
    ltc_insurance=0, pension_annual=0, other_income=0, filing_status='single'
):
    """Core function: Compute min assets, growth rate with MC."""
    ret_age = current_age + years_to_ret
    ss_age = current_age + years_to_ss
    ret_years = 120 - ret_age
    pre_ss_years = max(0, ss_age - ret_age)
    
    # SS benefit calculation (annual)
    if ss_age == 62:
        ss_annual = ss_min
    elif ss_age == fra_age:
        ss_annual = ss_fra
    elif ss_age == 70:
        ss_annual = ss_max
    else:
        months_from_fra = (ss_age - fra_age) * 12
        if months_from_fra < 0:  # Early
            months_early = abs(months_from_fra)
            reduction = min(36, months_early) * (5/9)/100 + max(0, months_early - 36) * (5/12)/100
            ss_annual = ss_fra * (1 - reduction)
        else:  # Delayed
            credit = min(months_from_fra, (70 - fra_age)*12) * (2/3)/100
            ss_annual = ss_fra * (1 + credit)
    
    # Annual needs projection
    annual_need_now = monthly_income * 12
    inflation_factors = [INFLATION_SHORT if i < 2 else INFLATION_LONG for i in range(years_to_ret + ret_years)]
    cum_infl_to_ret = np.prod(1 + np.array(inflation_factors[:years_to_ret]))
    annual_need_at_ret = annual_need_now * cum_infl_to_ret
    
    # Project annual needs, SS, pension, other during ret
    needs = [annual_need_at_ret * np.prod(1 + np.array(inflation_factors[years_to_ret:years_to_ret + k])) for k in range(1, ret_years + 1)]
    ss_series = [0] * pre_ss_years + [ss_annual * np.prod(1 + np.array([INFLATION_LONG] * (k - pre_ss_years))) for k in range(pre_ss_years + 1, ret_years + 1)]
    pension_series = [pension_annual * np.prod(1 + np.array([INFLATION_LONG] * k)) for k in range(1, ret_years + 1)]
    other_series = [other_income * np.prod(1 + np.array([INFLATION_LONG] * k)) for k in range(1, ret_years + 1)]
    
    # LTC projection (phased AI reduction after 5 years)
    ltc_needs = [max(0, LTC_BASE_COST * (1 + LTC_INFLATION)**k * (1 - AI_LTC_REDUCTION * min(1, k/ (ret_years/2))) - ltc_insurance) for k in range(1, ret_years + 1)]
    
    # Pre-tax gaps
    gaps = [needs[k] + ltc_needs[k] - ss_series[k] - pension_series[k] - other_series[k] for k in range(ret_years)]
    
    # Tax adjustment: Net to pre-tax withdrawals
    withdrawals = []
    for k in range(ret_years):
        age = ret_age + k
        total_income = gaps[k] + ss_series[k] + pension_series[k] + other_series[k]
        prov_income = total_income / 2 + ss_series[k] / 2
        taxable_ss = ss_series[k] * ss_taxable(prov_income)
        taxable_income = total_income + taxable_ss
        
        fed_tax = calculate_federal_tax(taxable_income, filing_status)
        ga_exclusion = GA_EXCLUSION_65PLUS if GA_RESIDENT and age >= 65 else 0
        ga_taxable = max(0, taxable_income - ga_exclusion)
        ga_tax = ga_taxable * GA_TAX_RATE
        total_tax = fed_tax + ga_tax
        
        pre_tax_withdrawal = gaps[k] + total_tax / (1 - (fed_tax / taxable_income if taxable_income else 0))
        withdrawals.append(pre_tax_withdrawal)
    
    # Deterministic PV for base assets at ret
    disc_factors = [(1 + POST_RET_RETURN_MEAN) / (1 + INFLATION_LONG) ** k for k in range(1, ret_years + 1)]
    assets_ret_det = sum(w / d for w, d in zip(withdrawals, disc_factors)) + legacy_desired / disc_factors[-1]
    
    # Monte Carlo for probabilistic
    success_rates = []
    asset_levels = np.linspace(assets_ret_det * 0.8, assets_ret_det * 1.5, 20)
    for assets_ret in asset_levels:
        successes = 0
        for _ in range(NUM_SIM):
            balance = assets_ret
            returns = norm.rvs(POST_RET_RETURN_MEAN, POST_RET_RETURN_SD, ret_years)
            infls = norm.rvs(INFLATION_LONG, 0.005, ret_years)
            exhausted = False
            for y in range(ret_years):
                balance *= (1 + returns[y])
                wd = withdrawals[y] * (1 + infls[y]) ** y
                if balance < wd:
                    exhausted = True
                    break
                balance -= wd
            if not exhausted and balance >= legacy_desired:
                successes += 1
        success_rates.append(successes / NUM_SIM)
    
    # Interp min assets for target prob
    assets_ret_prob = np.interp(SUCCESS_PROB, success_rates, asset_levels)
    
    # Back to current: Required growth rate
    min_assets_now = assets_ret_prob / (1 + 0.07) ** years_to_ret
    req_growth = (assets_ret_prob / min_assets_now) ** (1 / years_to_ret) - 1 if years_to_ret > 0 and min_assets_now > 0 else 0.07
    
    return {
        'min_assets_ret': assets_ret_prob,
        'min_assets_now': min_assets_now,
        'required_growth_rate': req_growth,
        'withdrawals': withdrawals,
        'needs': needs,
        'ss_series': ss_series,
        'pension_series': pension_series,
        'ltc_needs': ltc_needs,
        'success_rates': success_rates,
        'asset_levels': asset_levels
    }

def main():
    st.set_page_config(page_title="Retirement Income Calculator", layout="wide", page_icon="💰")
    
    # Enable iframe embedding
    st.markdown("""
        <script>
            window.parent.postMessage({type: 'streamlit:frameHeight', height: document.body.scrollHeight}, '*');
        </script>
    """, unsafe_allow_html=True)
    
    st.title("🏦 Retirement Income Calculator Dashboard")
    st.markdown("---")
    
    # Sidebar for inputs
    st.sidebar.header("Client Information")
    
    # Basic Demographics
    st.sidebar.subheader("Demographics")
    current_age = st.sidebar.slider("Current Age", 25, 80, 50)
    years_to_ret = st.sidebar.slider("Years to Retirement", 1, 50, 15)
    years_to_ss = st.sidebar.slider("Years to Social Security", 1, 50, 17)
    filing_status = st.sidebar.selectbox("Filing Status", ["single", "married"])
    
    # Income & Expenses
    st.sidebar.subheader("Income Needs")
    monthly_income = st.sidebar.number_input("Monthly Income Needed (today's $)", 1000, 50000, 5000, step=100)
    legacy_desired = st.sidebar.number_input("Desired Legacy Amount ($)", 0, 5000000, 0, step=10000)
    
    # Social Security
    st.sidebar.subheader("Social Security Benefits (Annual)")
    ss_min = st.sidebar.number_input("SS at Age 62", 0, 100000, 20000, step=1000)
    ss_fra = st.sidebar.number_input("SS at Full Retirement Age", 0, 100000, 30000, step=1000)
    ss_max = st.sidebar.number_input("SS at Age 70", 0, 100000, 40000, step=1000)
    fra_age = st.sidebar.selectbox("Full Retirement Age", [66, 67], index=1)
    
    # Other Income Sources
    st.sidebar.subheader("Other Income Sources (Annual)")
    pension_annual = st.sidebar.number_input("Pension Income", 0, 200000, 10000, step=1000)
    other_income = st.sidebar.number_input("Other Income", 0, 200000, 5000, step=1000)
    ltc_insurance = st.sidebar.number_input("LTC Insurance Coverage", 0, 200000, 50000, step=5000)
    
    # Calculate button
    if st.sidebar.button("Calculate Retirement Needs", type="primary"):
        with st.spinner("Calculating retirement projections..."):
            inputs = {
                'current_age': current_age,
                'years_to_ret': years_to_ret,
                'years_to_ss': years_to_ss,
                'monthly_income': monthly_income,
                'legacy_desired': legacy_desired,
                'ss_min': ss_min,
                'ss_fra': ss_fra,
                'ss_max': ss_max,
                'fra_age': fra_age,
                'ltc_insurance': ltc_insurance,
                'pension_annual': pension_annual,
                'other_income': other_income,
                'filing_status': filing_status
            }
            
            results = retirement_calculator(**inputs)
            
            # Display Results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Assets Needed at Retirement",
                    f"${results['min_assets_ret']:,.0f}",
                    help="Amount needed at retirement with 90% success probability"
                )
            
            with col2:
                st.metric(
                    "Assets Needed Today",
                    f"${results['min_assets_now']:,.0f}",
                    help="Present value of retirement assets needed"
                )
            
            with col3:
                st.metric(
                    "Required Growth Rate",
                    f"{results['required_growth_rate']:.1%}",
                    help="Annual return needed to reach retirement goal"
                )
            
            with col4:
                safe_withdrawal = results['min_assets_ret'] * SAFE_WITHDRAWAL_RATE
                st.metric(
                    "4% Withdrawal Amount",
                    f"${safe_withdrawal:,.0f}",
                    help="Annual income using 4% withdrawal rule"
                )
            
            # Charts section
            st.markdown("---")
            st.subheader("📊 Retirement Income Projections")
            
            # Create income breakdown chart
            retirement_years = list(range(current_age + years_to_ret, 120))
            
            # Prepare data for visualization
            chart_data = pd.DataFrame({
                'Age': retirement_years[:len(results['needs'])],
                'Total Needs': results['needs'],
                'Social Security': results['ss_series'],
                'Pension': results['pension_series'],
                'LTC Needs': results['ltc_needs'],
                'Portfolio Withdrawals': results['withdrawals']
            })
            
            # Income sources stacked chart
            fig_income = go.Figure()
            fig_income.add_trace(go.Scatter(x=chart_data['Age'], y=chart_data['Social Security'], 
                                          fill='tonexty', name='Social Security', 
                                          line=dict(color='lightblue')))
            fig_income.add_trace(go.Scatter(x=chart_data['Age'], y=chart_data['Pension'], 
                                          fill='tonexty', name='Pension',
                                          line=dict(color='lightgreen')))
            fig_income.add_trace(go.Scatter(x=chart_data['Age'], y=chart_data['Portfolio Withdrawals'], 
                                          fill='tonexty', name='Portfolio Withdrawals',
                                          line=dict(color='orange')))
            fig_income.add_trace(go.Scatter(x=chart_data['Age'], y=chart_data['Total Needs'], 
                                          name='Total Income Needs', mode='lines',
                                          line=dict(color='red', width=3, dash='dash')))
            
            fig_income.update_layout(
                title="Retirement Income Sources vs. Needs",
                xaxis_title="Age",
                yaxis_title="Annual Amount ($)",
                hovermode='x unified',
                yaxis=dict(tickformat='$,.0f')
            )
            
            st.plotly_chart(fig_income, use_container_width=True)
            
            # Success probability chart
            fig_prob = go.Figure()
            fig_prob.add_trace(go.Scatter(
                x=results['asset_levels'],
                y=[rate * 100 for rate in results['success_rates']],
                mode='lines+markers',
                name='Success Probability',
                line=dict(color='green', width=3)
            ))
            
            fig_prob.add_hline(y=90, line_dash="dash", line_color="red", 
                              annotation_text="90% Target")
            fig_prob.add_vline(x=results['min_assets_ret'], line_dash="dash", 
                              line_color="blue", annotation_text="Required Assets")
            
            fig_prob.update_layout(
                title="Monte Carlo Success Probability Analysis",
                xaxis_title="Assets at Retirement ($)",
                yaxis_title="Success Probability (%)",
                xaxis=dict(tickformat='$,.0f'),
                yaxis=dict(tickformat='.0f')
            )
            
            st.plotly_chart(fig_prob, use_container_width=True)
            
            # Summary table
            st.subheader("📋 Detailed Analysis Summary")
            summary_data = {
                'Metric': [
                    'Current Age',
                    'Retirement Age', 
                    'Social Security Age',
                    'Years in Retirement',
                    'Monthly Income Needed (Today)',
                    'Annual Income at Retirement',
                    'Assets Needed at Retirement',
                    'Assets Needed Today',
                    'Required Annual Return',
                    'First Year SS Benefit',
                    'Annual Pension Income',
                    'LTC Insurance Coverage'
                ],
                'Value': [
                    f"{current_age} years",
                    f"{current_age + years_to_ret} years",
                    f"{current_age + years_to_ss} years", 
                    f"{120 - (current_age + years_to_ret)} years",
                    f"${monthly_income:,}/month",
                    f"${results['needs'][0]:,.0f}",
                    f"${results['min_assets_ret']:,.0f}",
                    f"${results['min_assets_now']:,.0f}",
                    f"{results['required_growth_rate']:.2%}",
                    f"${results['ss_series'][max(0, current_age + years_to_ss - current_age - years_to_ret)]:,.0f}",
                    f"${pension_annual:,}",
                    f"${ltc_insurance:,}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.table(summary_df)
            
    else:
        st.info("👈 Please enter client information in the sidebar and click 'Calculate Retirement Needs' to begin analysis.")

if __name__ == "__main__":
    main()