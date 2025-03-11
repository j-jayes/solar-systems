import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Initialize session state
for key, default in zip(['solar_kw', 'battery_kwh', 'inverter_kva', 'daily_usage_kwh', 'total_cost'], [8, 75, 10, 30, 0]):
    if key not in st.session_state:
        st.session_state[key] = default

# --- System Specification & Cost Tab ---
def system_specifications():
    st.header("Solar PV and Battery System Specifications")

    st.sidebar.header("System Specifications")

    st.session_state.daily_usage_kwh = st.sidebar.number_input(
        "Daily Electricity Consumption (kWh)", 5, 100, st.session_state.daily_usage_kwh, 5)
    backup_hours = st.sidebar.slider("Backup Duration (hours)", 12, 72, 48, step=12)
    
    st.session_state.solar_kw = st.sidebar.number_input(
        "Solar Panel Array Size (kWp)", 1, 20, st.session_state.solar_kw, step=1)
    st.session_state.battery_kwh = st.sidebar.number_input(
        "Battery Capacity (kWh)", 5, 150, st.session_state.battery_kwh, step=5)
    st.session_state.inverter_kva = st.sidebar.number_input(
        "Inverter Size (kVA)", 3, 15, st.session_state.inverter_kva, step=1)
    
    st.markdown(f"""
    ### System Requirements
    - Daily Electricity Consumption: **{st.session_state.daily_usage_kwh} kWh**
    - Backup Duration: **{backup_hours} hours**
    - Solar Panel Array: **{st.session_state.solar_kw} kWp** (~{st.session_state.solar_kw * 2.5} × 400W panels)
    - Battery Capacity: **{st.session_state.battery_kwh} kWh**
    - Hybrid Inverter: **{st.session_state.inverter_kva} kVA**
    """)

    cost_panels = st.session_state.solar_kw * 10000
    cost_battery = st.session_state.battery_kwh * 1333
    cost_inverter = st.session_state.inverter_kva * 2000
    cost_installation = 20000

    data = {
        "Component": ["Solar Panels", "Battery", "Hybrid Inverter & Controller", "Installation & Misc."],
        "Cost (ZAR)": [cost_panels, cost_battery, cost_inverter, cost_installation]
    }

    df = pd.DataFrame(data)

    st.subheader("System Component Costs")
    st.dataframe(df.style.format({"Cost (ZAR)": "{:,.0f}"}))

    st.session_state.total_cost = df['Cost (ZAR)'].sum()
    st.markdown(f"**Total Estimated Cost: R{st.session_state.total_cost:,.0f}**")


# --- Financial Model Tab ---
def financial_model():
    st.header("Financial Payback Model")

    st.markdown("### Financial Assumptions")

    electricity_cost = st.sidebar.number_input("Electricity Cost per kWh (R)", 1.0, 10.0, 3.35, 0.1)
    inflation_rate = st.sidebar.number_input("Annual Electricity Price Inflation (%)", 0.0, 20.0, 5.0, 0.5) / 100
    opportunity_cost_rate = st.sidebar.number_input("Real Opportunity Cost of Capital (%)", 0.0, 10.0, 2.0, 0.1) / 100
    sell_to_grid = st.sidebar.checkbox("Allow Selling Excess to Grid?", False)
    sell_back_rate = st.sidebar.number_input("Grid Sell-back Rate (%)", 0.0, 100.0, 15.0, 5.0) / 100 if sell_to_grid else 0

    years = 25
    annual_usage_kwh = st.session_state.daily_usage_kwh * 365

    annual_savings_list = []
    cumulative_net = []  
    investment_net = []  # For comparing with investment opportunity

    # Access the total_cost from session state
    total_cost = st.session_state.total_cost

    for year in range(years):
        current_price = electricity_cost * (1 + inflation_rate)**year
        annual_savings = annual_usage_kwh * current_price

        if sell_to_grid:
            annual_savings += annual_usage_kwh * 0.2 * sell_back_rate * current_price  # Assuming 20% excess

        opportunity_cost = total_cost * ((1 + opportunity_cost_rate) ** year - 1)
        
        annual_savings_list.append(annual_savings)
        cumulative_savings = sum(annual_savings_list)
        
        # First method: Simple payback (savings vs. initial cost)
        net_savings = cumulative_savings - total_cost
        cumulative_net.append(net_savings)
        
        # Second method: Compare with investment opportunity
        investment_value = total_cost * (1 + opportunity_cost_rate) ** year
        investment_comparison = cumulative_savings - investment_value
        investment_net.append(investment_comparison)

    df_model = pd.DataFrame({
        "Year": np.arange(1, years + 1),
        "Cumulative Savings (R)": np.cumsum(annual_savings_list),
        "Opportunity Cost (R)": [total_cost * ((1 + opportunity_cost_rate) ** y - 1) for y in range(years)],
        "Simple Net Savings (R)": cumulative_net,
        "Net vs Investment (R)": investment_net
    })

    # Plot main financial analysis
    fig = px.line(df_model, x="Year", y=["Cumulative Savings (R)", "Opportunity Cost (R)", "Simple Net Savings (R)"],
                  title="Financial Model: Solar Payback Analysis",
                  labels={"value": "Rand", "Year": "Year"})

    st.plotly_chart(fig, use_container_width=True)

    # Calculate and display both payback periods
    simple_payback_year = next((year for year, net in enumerate(cumulative_net, 1) if net >= 0), None)
    investment_payback_year = next((year for year, net in enumerate(investment_net, 1) if net >= 0), None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if simple_payback_year:
            st.success(f"**Simple Payback Period: {simple_payback_year:.1f} years**")
            st.caption("Time until electricity savings cover the initial system cost")
        else:
            st.warning("System does not achieve simple payback within modelled period.")
    
    with col2:
        if investment_payback_year:
            st.info(f"**Investment-Adjusted Payback: {investment_payback_year:.1f} years**")
            st.caption("Time until savings exceed what you would earn investing the same amount")
        else:
            st.warning("System does not outperform alternative investment within modelled period.")
    
    st.markdown("---")
    st.markdown("### Investment Comparison")
    st.markdown("""
    The **Simple Payback Period** compares the cumulative electricity savings directly against the initial system cost.
    
    The **Investment-Adjusted Payback** compares the savings against what the same money would earn if invested at your specified opportunity cost rate.
    """)
    
    # Plot investment comparison
    fig2 = px.line(df_model, x="Year", y=["Simple Net Savings (R)", "Net vs Investment (R)"],
                  title="Solar System vs Alternative Investment",
                  labels={"value": "Rand", "Year": "Year"})
    fig2.update_layout(legend=dict(
        title="Comparison Metrics",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    
    st.plotly_chart(fig2, use_container_width=True)


# --- Streamlit App Main ---
def main():
    st.title("Solar Energy Financial Modelling Tool")

    tabs = st.tabs(["System Specifications", "Financial Analysis"])

    with tabs[0]:
        system_specifications()

    with tabs[1]:
        financial_model()

if __name__ == "__main__":
    main()