import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

# Set custom theme for all plotly figures
pio.templates.default = "plotly_white"

# Custom CSS to make the app look modern with Lato and IBM Plex Mono fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Lato', sans-serif;
        font-weight: 400;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lato', sans-serif;
        font-weight: 700;
    }
    
    .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2 {
        color: #1e3a8a; /* Tailwind blue-900 */
    }
    
    /* Tailwind-like shadow */
    .streamlit-card {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #fff;
        border: 1px solid #e5e7eb;
    }
    
    /* Number styling */
    .mono-nums {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2563eb; /* Tailwind blue-600 */
        color: white;
        border: none;
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8; /* Tailwind blue-700 */
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc; /* Tailwind slate-50 */
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: #334155; /* Tailwind slate-700 */
    }
    
    /* Success/Info message styling */
    .st-emotion-cache-16idsys p {
        font-weight: 600;
    }
    
    /* Make dataframes look better */
    .dataframe {
        border: none !important;
    }
    
    .dataframe tbody tr:nth-of-type(even) {
        background-color: #f1f5f9 !important; /* Tailwind slate-100 */
    }
    
    .dataframe th {
        background-color: #1e293b !important; /* Tailwind slate-800 */
        color: white !important;
        padding: 0.75rem 1rem !important;
        border: none !important;
    }
    
    .dataframe td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid #e2e8f0 !important; /* Tailwind slate-200 */
        border-right: none !important;
        border-left: none !important;
    }
    
    /* Format numbers to use IBM Plex Mono */
    .mono-nums, td:has(.mono-nums) {
        font-family: 'IBM Plex Mono', monospace !important;
        font-feature-settings: "tnum" !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
# Initialize session state
for key, default in zip(['solar_kw', 'battery_kwh', 'inverter_kva', 'daily_usage_kwh', 'total_cost'], [8, 50, 5, 20, 0]):
    if key not in st.session_state:
        st.session_state[key] = default

# --- System Specifications ---
def system_specifications():
    st.header("Solar PV and Battery System Specifications")

    st.sidebar.header("System Inputs")

    daily_usage = st.sidebar.number_input(
        "Daily Electricity Consumption (kWh)", 5, 100, 20, 5)

    # Changed from days to hours - using a slider with hours
    backup_hours = st.sidebar.slider("Backup Duration (Hours)", 0, 72, 12, 6)
    
    # Convert hours to fraction of a day for calculations
    backup_days = backup_hours / 24
    
    battery_dod = 0.8  # Fixed at 80%

    avg_sun_hours = st.sidebar.slider("Avg Peak Sun Hours/day", 4.5, 6.0, 5.0, 0.1)

    # Calculations
    battery_capacity = (daily_usage * backup_days) / battery_dod
    solar_kw_required = daily_usage / avg_sun_hours
    
    # Round solar capacity up to nearest 0.5
    solar_kw = np.ceil(solar_kw_required * 2) / 2
    
    # Calculate inverter size
    inverter_size = np.ceil(daily_usage * 1.25 / 5)

    # Update Session State
    st.session_state.update({
        "daily_usage_kwh": daily_usage,
        "battery_kwh": np.ceil(battery_capacity / 5) * 5,  # nearest 5 kWh
        "solar_kw": solar_kw,
        "inverter_kva": inverter_size
    })

    st.markdown("### Recommended System")
    st.markdown(f"""
    - **Daily Usage:** {daily_usage} kWh/day
    - **Backup Duration:** {backup_hours} hours
    - **Battery (80% DoD):** {st.session_state.battery_kwh:.1f} kWh
    - **Solar Array:** {solar_kw} kWp (~{int(solar_kw * 2.5)} × 400W panels)
    - **Inverter Size:** {inverter_size:.1f} kVA
    """)

    # Cost Calculations
    cost_panels = solar_kw * 12000  # ZAR per kWp
    cost_battery = st.session_state.battery_kwh * 5000  # ZAR per kWh
    cost_inverter = inverter_size * 3500  # ZAR per kVA
    cost_installation = 20000

    # Create DataFrame for costs
    cost_df = pd.DataFrame({
        "Component": ["Solar Panels", "Battery Storage", "Hybrid Inverter", "Installation & Misc."],
        "Cost (ZAR)": [cost_panels, cost_battery, cost_inverter, cost_installation]
    })

    st.subheader("System Component Costs")
    st.dataframe(cost_df.style.format({"Cost (ZAR)": "{:,.0f}"}))

    total_cost = cost_df['Cost (ZAR)'].sum()
    st.session_state.total_cost = total_cost
    st.markdown(f"### **Total Estimated Cost: ZAR {total_cost:,.0f}**")

# --- Information and Guidance Tab ---
def information_tab():
    st.header("Information and Assumptions")

    st.markdown("""
    ### System Assumptions
    - **Battery Depth-of-Discharge (DoD):** 80%, common for Lithium-ion batteries (LiFePO4).
    - **Average Peak Sun Hours:** Typical values in South Africa range from **4.5 to 6 hours/day**.

    ### Component Sizing Logic
    - **Battery Capacity:** Calculated based on your daily usage and desired backup duration.  
      Battery Size (kWh) = Daily Usage (kWh) × Backup Days ÷ DoD (0.8)
                
    - **Battery Sizing** Battery capacity is rounded up to the nearest 5 kWh increment

    - **Solar Panel Array Size:** Based on typical solar insolation in South Africa (5 kWh/day/kWp).  
      Solar Size (kWp) = Daily Usage (kWh) ÷ Peak Sun Hours (4.5–6)

    - **Inverter Size:** We divide the daily usage by 5 kWh to get a rough kVA estimate of the peak load, and multiply by 1.25 for a safety factor.
                Inverters commonly come in sizes like 3.6, 5, 8, etc. kVA. TODO: Add more explanation
                
    ### Financial Assumptions
    - Costs are indicative averages for residential solar installations in South Africa, as researched by GPT 4.5 Deep Research.
    - Solar Panels: ZAR 12,000 per kWp
    - Battery Storage: ZAR 5,000 per kWh
    - Hybrid Inverter: ZAR 3,500 per kVA
    - Installation & Misc.: ZAR 20,000
    - **Electricity Cost:** ZAR 3.35 per kWh (Eskom rates for Ethekwini Municipality)
    - **Annual Inflation:** 5% (This could be even higher in the future)
    - **Opportunity Cost of Capital:** 5% (Your expected return on investment)
    - **Grid Sell-back Rate:** 15% (No idea about this, need to check the NERSA documentation)
                
    ### What is left out?
    - **Maintenance Costs:** Solar systems require minimal maintenance, but it's not zero.
    - **Battery Degradation:** Batteries lose capacity over time, especially if not cycled regularly.
    - **Timing of consumption:** This model assumes you consume all the solar power you generate, and does not account for variations in tariff by time-of-use or season.

    This tool provides an indicative analysis. Consult a professional installer for exact sizing.
    """)

# --- Financial Model Tab ---
def financial_model():
    st.header("Financial Payback Model")

    st.markdown("### Financial Assumptions")

    electricity_cost = st.sidebar.number_input("Electricity Cost per kWh (R)", 1.0, 10.0, 3.35, 0.1)
    inflation_rate = st.sidebar.number_input("Annual Electricity Price Inflation (%)", 0.0, 20.0, 5.0, 0.5) / 100
    opportunity_cost_rate = st.sidebar.number_input("Real Opportunity Cost of Capital (%)", 0.0, 10.0, 5.0, 0.1) / 100
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
        # "Cumulative Savings (R)": np.cumsum(annual_savings_list),
        "Opportunity Cost (R)": [total_cost * ((1 + opportunity_cost_rate) ** y - 1) for y in range(years)],
        "Simple Net Savings (R)": cumulative_net,
        "Net vs Investment (R)": investment_net
    })

    # Plot main financial analysis
    fig = px.line(df_model, x="Year", y=[
        # "Cumulative Savings (R)", 
        "Opportunity Cost (R)", "Simple Net Savings (R)"],
                  title="Financial Model: Solar Payback Analysis",
                  labels={"value": "Rand", "Year": "Year"})
    
        # Add horizontal line at y=0
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=years,
        y1=0,
        line=dict(
            color="gray",
            width=1.5,
            dash="dash",
        ),
        layer="below"
    )

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

    # Add horizontal line at y=0
    fig2.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=years,
        y1=0,
        line=dict(
            color="gray",
            width=1.5,
            dash="dash",
        ),
        layer="below"
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# --- Streamlit App Main ---
def main():
    st.title("Solar Energy Financial Modelling Tool")

    tabs = st.tabs(["System Specifications", "Financial Analysis", "Info & Assumptions"])

    with tabs[0]:
        system_specifications()

    with tabs[1]:
        financial_model()

    with tabs[2]:
        information_tab()

if __name__ == "__main__":
    main()