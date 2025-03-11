import streamlit as st
import pandas as pd
import numpy as np

# Set page title and configuration
st.set_page_config(page_title="Equity Option Calculator", layout="wide")
st.title("Equity Option Calculator")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

# Get redemption percentage (0-10% in 1% increments)
redemption_percentage = st.sidebar.slider(
    "A-Share/Options Redemption Percentage", 
    min_value=0, 
    max_value=10,
    value=5,
    step=1,
    help="Percentage of vested unsold A-Share/Options to redeem each year"
) / 100

# Get PBT growth rate (0-20% in 1% increments)
pbt_growth_rate = st.sidebar.slider(
    "PBT Growth Rate", 
    min_value=0, 
    max_value=20,
    value=15,
    step=1,
    help="Annual growth rate of share price"
) / 100

# Get strike price - UPDATED DEFAULT TO £6.00
strike_price = st.sidebar.number_input(
    "Strike Price (£)",
    min_value=0.01,
    value=6.00,
    step=0.01,
    format="%.2f",
    help="Initial strike price of options"
)

# Get total grant shares
total_grant_shares = st.sidebar.number_input(
    "Total Grant Shares",
    min_value=1,
    value=10000,
    step=100,
    help="Total number of shares in the grant"
)

# NEW: Common Share Inputs
st.sidebar.header("Common Share Parameters")

# Get total common shares
total_common_shares = st.sidebar.number_input(
    "Total Common Shares",
    min_value=1,
    value=10000,
    step=100,
    help="Total number of common shares"
)

# Get common share purchase price
common_purchase_price = st.sidebar.number_input(
    "Common Share Purchase Price (£)",
    min_value=0.01,
    value=2.00,
    step=0.01,
    format="%.2f",
    help="Initial purchase price of common shares"
)

# Get common share redemption percentage
common_redemption_percentage = st.sidebar.slider(
    "Common Share Redemption Percentage", 
    min_value=0, 
    max_value=10,
    value=5,
    step=1,
    help="Percentage of common shares to redeem each year starting from 2026"
) / 100

# Vesting schedule inputs
st.sidebar.header("Vesting Schedule")
vesting_method = st.sidebar.radio(
    "Vesting Method",
    ["Default Schedule", "Custom Vesting"],
    help="Choose default vesting schedule or set custom values"
)

# Initialize vested_shares_input dictionary
vested_shares_input = {}

if vesting_method == "Default Schedule":
    vested_shares_input = {
        2025: 6000,
        2026: 7000,
        2027: 8000,
        2028: 9000,
        2029: 10000,
        2030: 10000,
        2031: 10000,
        2032: 10000,
        2033: 10000,
        2034: 10000,
        2035: 10000
    }
    
    # Display the default schedule
    st.sidebar.write("Default vesting schedule:")
    default_schedule = pd.DataFrame({"Year": vested_shares_input.keys(), 
                                    "Vested Shares": vested_shares_input.values()})
    st.sidebar.dataframe(default_schedule, hide_index=True)
    
else:
    # Custom vesting inputs
    st.sidebar.write("Enter vested shares for each year:")
    
    # Use columns for more compact layout
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        vested_shares_input[2025] = st.number_input("2025", min_value=0, max_value=int(total_grant_shares), value=6000, step=100)
        vested_shares_input[2026] = st.number_input("2026", min_value=0, max_value=int(total_grant_shares), value=7000, step=100)
        vested_shares_input[2027] = st.number_input("2027", min_value=0, max_value=int(total_grant_shares), value=8000, step=100)
        vested_shares_input[2028] = st.number_input("2028", min_value=0, max_value=int(total_grant_shares), value=9000, step=100)
        vested_shares_input[2029] = st.number_input("2029", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)
        vested_shares_input[2030] = st.number_input("2030", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)
    
    with col2:
        vested_shares_input[2031] = st.number_input("2031", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)
        vested_shares_input[2032] = st.number_input("2032", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)
        vested_shares_input[2033] = st.number_input("2033", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)
        vested_shares_input[2034] = st.number_input("2034", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)
        vested_shares_input[2035] = st.number_input("2035", min_value=0, max_value=int(total_grant_shares), value=10000, step=100)

# Display the main parameters
st.write("### A-Share/Options Parameters")
st.write(f"- **A-Share/Options Redemption Rate**: {redemption_percentage*100:.0f}%")
st.write(f"- **PBT Growth Rate**: {pbt_growth_rate*100:.0f}%")
st.write(f"- **Strike Price**: £{strike_price:.2f}")
st.write(f"- **Total Grant Shares**: {total_grant_shares:,}")

# Display common share parameters
st.write("### Common Share Parameters")
st.write(f"- **Common Share Redemption Rate**: {common_redemption_percentage*100:.0f}%")
st.write(f"- **Common Share Purchase Price**: £{common_purchase_price:.2f}")
st.write(f"- **Total Common Shares**: {total_common_shares:,}")

try:
    # Calculate values with specific redemption and growth rates WITHOUT ANY ROUNDING
    def calculate_values(redemption_pct, growth_pct, vesting_input, common_redemption_pct, common_shares, common_price):
        # Initialize dataframe for years 2024-2035
        years = list(range(2024, 2036))
        df = pd.DataFrame(index=years)
        
        # Initialize all columns with zeros to ensure consistency
        # Option shares columns
        df['Share Price'] = 0.0
        df['Vested Shares'] = 0
        df['Vested Unsold Shares'] = 0.0
        df['Redeemed Shares'] = 0.0
        df['Cumulative Redeemed'] = 0.0
        df['Unsold Shares'] = 0.0
        df['Redemption Value'] = 0.0
        df['Cumulative Redemption Value'] = 0.0
        df['Value of Unsold Shares'] = 0.0
        df['Total Grant Value'] = 0.0
        
        # Common shares columns
        df['Common Shares Redeemed'] = 0.0
        df['Cumulative Common Redeemed'] = 0.0
        df['Unsold Common Shares'] = 0.0
        df['Common Redemption Value'] = 0.0
        df['Cumulative Common Redemption Value'] = 0.0
        df['Value of Unsold Common Shares'] = 0.0
        df['Total Common Share Value'] = 0.0
        
        # Combined total value
        df['Combined Total Value'] = 0.0
        
        # Initial values for 2024
        df.loc[2024, 'Share Price'] = strike_price
        df.loc[2024, 'Vested Shares'] = 0
        df.loc[2024, 'Vested Unsold Shares'] = 0
        df.loc[2024, 'Redeemed Shares'] = 0
        df.loc[2024, 'Cumulative Redeemed'] = 0
        df.loc[2024, 'Unsold Shares'] = total_grant_shares
        df.loc[2024, 'Redemption Value'] = 0.0
        df.loc[2024, 'Cumulative Redemption Value'] = 0.0
        df.loc[2024, 'Value of Unsold Shares'] = 0.0
        df.loc[2024, 'Total Grant Value'] = 0.0
        
        # Initial values for common shares in 2024
        df.loc[2024, 'Common Shares Redeemed'] = 0
        df.loc[2024, 'Cumulative Common Redeemed'] = 0
        df.loc[2024, 'Unsold Common Shares'] = common_shares
        df.loc[2024, 'Common Redemption Value'] = 0.0
        df.loc[2024, 'Cumulative Common Redemption Value'] = 0.0
        df.loc[2024, 'Value of Unsold Common Shares'] = 0.0
        df.loc[2024, 'Total Common Share Value'] = 0.0
        df.loc[2024, 'Combined Total Value'] = 0.0
        
        # Year 2025 calculations (no redemption in first year)
        # Exact share price calculation: previous price * (1 + growth rate)
        df.loc[2025, 'Share Price'] = df.loc[2024, 'Share Price'] * (1 + growth_pct)
        df.loc[2025, 'Vested Shares'] = vesting_input[2025]
        df.loc[2025, 'Redeemed Shares'] = 0
        df.loc[2025, 'Cumulative Redeemed'] = 0
        df.loc[2025, 'Vested Unsold Shares'] = df.loc[2025, 'Vested Shares'] - df.loc[2025, 'Cumulative Redeemed']
        df.loc[2025, 'Unsold Shares'] = df.loc[2024, 'Unsold Shares']
        share_price_diff = max(0, df.loc[2025, 'Share Price'] - strike_price)
        df.loc[2025, 'Redemption Value'] = 0.0
        df.loc[2025, 'Cumulative Redemption Value'] = 0.0
        df.loc[2025, 'Value of Unsold Shares'] = share_price_diff * df.loc[2025, 'Unsold Shares']
        df.loc[2025, 'Total Grant Value'] = df.loc[2025, 'Cumulative Redemption Value'] + df.loc[2025, 'Value of Unsold Shares']
        
        # Common shares calculation for 2025 (no redemption yet)
        df.loc[2025, 'Common Shares Redeemed'] = 0
        df.loc[2025, 'Cumulative Common Redeemed'] = 0
        df.loc[2025, 'Unsold Common Shares'] = common_shares
        common_price_diff = max(0, df.loc[2025, 'Share Price'] - common_price)
        df.loc[2025, 'Common Redemption Value'] = 0.0
        df.loc[2025, 'Cumulative Common Redemption Value'] = 0.0
        df.loc[2025, 'Value of Unsold Common Shares'] = common_price_diff * df.loc[2025, 'Unsold Common Shares']
        df.loc[2025, 'Total Common Share Value'] = df.loc[2025, 'Cumulative Common Redemption Value'] + df.loc[2025, 'Value of Unsold Common Shares']
        
        # Combined total for 2025
        df.loc[2025, 'Combined Total Value'] = df.loc[2025, 'Total Grant Value'] + df.loc[2025, 'Total Common Share Value']
        
        # Calculate for years 2026-2035
        for year in range(2026, 2036):
            # Exact share price calculation: previous price * (1 + growth rate)
            # No rounding at any stage to maintain full precision
            df.loc[year, 'Share Price'] = df.loc[year-1, 'Share Price'] * (1 + growth_pct)
            
            # Option Shares Calculations - according to the clarified rule
            # Vested shares from input
            df.loc[year, 'Vested Shares'] = vesting_input[year]
            
            # Redeemed shares for this year - based on PREVIOUS year's VESTED UNSOLD SHARES
            df.loc[year, 'Redeemed Shares'] = df.loc[year-1, 'Vested Unsold Shares'] * redemption_pct
            
            # Update cumulative redeemed
            df.loc[year, 'Cumulative Redeemed'] = df.loc[year-1, 'Cumulative Redeemed'] + df.loc[year, 'Redeemed Shares']
            
            # Vested unsold shares = vested shares - cumulative redeemed
            df.loc[year, 'Vested Unsold Shares'] = df.loc[year, 'Vested Shares'] - df.loc[year, 'Cumulative Redeemed']
            df.loc[year, 'Vested Unsold Shares'] = max(0, df.loc[year, 'Vested Unsold Shares'])
            
            # Unsold shares = total shares minus cumulative redeemed
            df.loc[year, 'Unsold Shares'] = total_grant_shares - df.loc[year, 'Cumulative Redeemed']
            
            # Redemption value = (share price - strike price) * redeemed shares
            share_price_diff = max(0, df.loc[year, 'Share Price'] - strike_price)
            df.loc[year, 'Redemption Value'] = share_price_diff * df.loc[year, 'Redeemed Shares']
            
            # Cumulative redemption value
            df.loc[year, 'Cumulative Redemption Value'] = df.loc[year-1, 'Cumulative Redemption Value'] + df.loc[year, 'Redemption Value']
            
            # Value of unsold shares = (share price - strike price) * unsold shares
            df.loc[year, 'Value of Unsold Shares'] = share_price_diff * df.loc[year, 'Unsold Shares']
            
            # Total grant value = cumulative redemption value + value of unsold shares
            df.loc[year, 'Total Grant Value'] = df.loc[year, 'Cumulative Redemption Value'] + df.loc[year, 'Value of Unsold Shares']
            
            # Common Shares Calculations - redemption starts in 2026
            # Common shares redeemed (% of previous year's unsold common shares) - exact calculation, no rounding
            df.loc[year, 'Common Shares Redeemed'] = df.loc[year-1, 'Unsold Common Shares'] * common_redemption_pct
            
            # Cumulative common shares redeemed - exact calculation, no rounding
            df.loc[year, 'Cumulative Common Redeemed'] = df.loc[year-1, 'Cumulative Common Redeemed'] + df.loc[year, 'Common Shares Redeemed']
            
            # Unsold common shares - exact calculation, no rounding
            df.loc[year, 'Unsold Common Shares'] = common_shares - df.loc[year, 'Cumulative Common Redeemed']
            
            # Common redemption value = (share price - common purchase price) * common shares redeemed
            common_price_diff = max(0, df.loc[year, 'Share Price'] - common_price)
            df.loc[year, 'Common Redemption Value'] = common_price_diff * df.loc[year, 'Common Shares Redeemed']
            
            # Cumulative common redemption value
            df.loc[year, 'Cumulative Common Redemption Value'] = df.loc[year-1, 'Cumulative Common Redemption Value'] + df.loc[year, 'Common Redemption Value']
            
            # Value of unsold common shares
            df.loc[year, 'Value of Unsold Common Shares'] = common_price_diff * df.loc[year, 'Unsold Common Shares']
            
            # Total common share value
            df.loc[year, 'Total Common Share Value'] = df.loc[year, 'Cumulative Common Redemption Value'] + df.loc[year, 'Value of Unsold Common Shares']
            
            # Combined total value
            df.loc[year, 'Combined Total Value'] = df.loc[year, 'Total Grant Value'] + df.loc[year, 'Total Common Share Value']
        
        return df

    # Main results with user-selected parameters
    results = calculate_values(
        redemption_percentage, 
        pbt_growth_rate, 
        vested_shares_input, 
        common_redemption_percentage,
        total_common_shares,
        common_purchase_price
    )
    
    # Display A-Share/Options results table summary only
    st.write("### Summary of A-Share/Options Value")
    filtered_option_results = results.loc[2025:, ['Share Price', 'Cumulative Redemption Value', 'Total Grant Value']]
    filtered_option_results = filtered_option_results.rename(columns={
        'Share Price': 'Share Repurchase Price (£)',
        'Cumulative Redemption Value': 'Proceeds from A-Share/Options Redemption (£)',
        'Total Grant Value': 'Total A-Share/Options Value (£)'
    })
    
    # Format for display
    display_option_df = filtered_option_results.copy()
    
    # Format indices as strings ('2025', '2026', etc.)
    display_option_df.index = display_option_df.index.map(lambda x: f'{x}')
    
    # Format share price with 2 decimal places
    display_option_df['Share Repurchase Price (£)'] = display_option_df['Share Repurchase Price (£)'].apply(lambda x: f"£{x:.2f}")
    
    # Format other columns with NO decimal places, only thousands separator
    for col in ['Proceeds from A-Share/Options Redemption (£)', 'Total A-Share/Options Value (£)']:
        display_option_df[col] = display_option_df[col].apply(lambda x: f"£{int(x):,}")
    
    # Display the option summary table
    st.dataframe(display_option_df, use_container_width=True)
    
    # Display Common Share results table summary only
    st.write("### Summary of Common Share Value")
    filtered_common_results = results.loc[2025:, ['Share Price', 'Cumulative Common Redemption Value', 'Total Common Share Value']]
    filtered_common_results = filtered_common_results.rename(columns={
        'Share Price': 'Share Repurchase Price (£)',
        'Cumulative Common Redemption Value': 'Proceeds from Common Share Redemption (£)',
        'Total Common Share Value': 'Total Common Share Value (£)'
    })
    
    # Format for display
    display_common_df = filtered_common_results.copy()
    
    # Format indices as strings ('2025', '2026', etc.)
    display_common_df.index = display_common_df.index.map(lambda x: f'{x}')
    
    # Format share price with 2 decimal places
    display_common_df['Share Repurchase Price (£)'] = display_common_df['Share Repurchase Price (£)'].apply(lambda x: f"£{x:.2f}")
    
    # Format other columns with NO decimal places, only thousands separator
    for col in ['Proceeds from Common Share Redemption (£)', 'Total Common Share Value (£)']:
        display_common_df[col] = display_common_df[col].apply(lambda x: f"£{int(x):,}")
    
    # Display the common share summary table
    st.dataframe(display_common_df, use_container_width=True)
    
    # Display Combined Total Value table
    st.write("### Combined Total Value (Options + Common Shares)")
    
    # Filter to only show 2025 onwards and the combined value
    filtered_combined_results = results.loc[2025:, ['Combined Total Value']]
    filtered_combined_results = filtered_combined_results.rename(columns={
        'Combined Total Value': 'Combined Total Value (£)'
    })
    
    # Format for display
    display_combined_df = filtered_combined_results.copy()
    
    # Format indices as strings ('2025', '2026', etc.)
    display_combined_df.index = display_combined_df.index.map(lambda x: f'{x}')
    
    # Format combined value with NO decimal places, only thousands separator
    display_combined_df['Combined Total Value (£)'] = display_combined_df['Combined Total Value (£)'].apply(lambda x: f"£{int(x):,}")
    
    # Display the combined results table
    st.dataframe(display_combined_df, use_container_width=True)
    
    # Download button for detailed results
    csv = results.to_csv(index=True)
    st.download_button(
        label="Download detailed results as CSV",
        data=csv,
        file_name="equity_redemption_results.csv",
        mime="text/csv",
    )
    
    # CHART 1: PBT Growth fixed at 20%, varying redemption rates for Options
    st.write("### Option Grant Value at Various Redemption Rates")
    st.write("*PBT Growth Rate fixed at 20%*")
    
    # Calculate data for different redemption rates using the user's vesting schedule
    chart1_data = pd.DataFrame(index=range(2025, 2036))
    
    # Add lines for different redemption rates
    redemption_rates = [0.0, 0.05, 0.10]
    for rate in redemption_rates:
        results_for_rate = calculate_values(
            rate, 
            0.20, 
            vested_shares_input,
            common_redemption_percentage,
            total_common_shares,
            common_purchase_price
        )
        chart1_data[f"{int(rate*100)}% Option Redemption"] = results_for_rate.loc[2025:2035, 'Total Grant Value']
    
    # Convert index to strings for better display
    chart1_data.index = chart1_data.index.map(str)
    
    # Display the chart
    st.line_chart(chart1_data)
    
    # Display 2035 values in a table for Chart 1
    st.write("**Final 2035 Values:**")
    final_values1 = pd.DataFrame({
        'Option Redemption Rate': [f"{int(rate*100)}%" for rate in redemption_rates],
        'Total Option Value (£)': [
            f"£{int(calculate_values(rate, 0.20, vested_shares_input, common_redemption_percentage, total_common_shares, common_purchase_price).loc[2035, 'Total Grant Value']):,}" 
            for rate in redemption_rates
        ]
    })
    st.table(final_values1)
    
    # CHART 2: Common Share Redemption rates comparison
    st.write("### Common Share Value at Various Redemption Rates")
    st.write("*PBT Growth Rate fixed at 20%*")
    
    # Calculate data for different common share redemption rates
    chart2_data = pd.DataFrame(index=range(2025, 2036))
    
    # Add lines for different common redemption rates
    common_redemption_rates = [0.0, 0.05, 0.10]
    for rate in common_redemption_rates:
        results_for_rate = calculate_values(
            redemption_percentage, 
            0.20, 
            vested_shares_input,
            rate,
            total_common_shares,
            common_purchase_price
        )
        chart2_data[f"{int(rate*100)}% Common Redemption"] = results_for_rate.loc[2025:2035, 'Total Common Share Value']
    
    # Convert index to strings for better display
    chart2_data.index = chart2_data.index.map(str)
    
    # Display the chart
    st.line_chart(chart2_data)
    
    # Display 2035 values in a table for Chart 2
    st.write("**Final 2035 Values:**")
    final_values2 = pd.DataFrame({
        'Common Share Redemption Rate': [f"{int(rate*100)}%" for rate in common_redemption_rates],
        'Total Common Share Value (£)': [
            f"£{int(calculate_values(redemption_percentage, 0.20, vested_shares_input, rate, total_common_shares, common_purchase_price).loc[2035, 'Total Common Share Value']):,}" 
            for rate in common_redemption_rates
        ]
    })
    st.table(final_values2)
    
    # CHART 3: Combined Value with different growth rates
    st.write("### Combined Total Value at Various PBT Growth Rates")
    st.write(f"*Option Redemption: {redemption_percentage*100:.0f}%, Common Redemption: {common_redemption_percentage*100:.0f}%*")
    
    # Calculate data for different growth rates
    chart3_data = pd.DataFrame(index=range(2025, 2036))
    
    # Add lines for different growth rates
    growth_rates = [0.15, 0.20]
    for rate in growth_rates:
        results_for_growth = calculate_values(
            redemption_percentage, 
            rate, 
            vested_shares_input,
            common_redemption_percentage,
            total_common_shares,
            common_purchase_price
        )
        chart3_data[f"{int(rate*100)}% Growth"] = results_for_growth.loc[2025:2035, 'Combined Total Value']
    
    # Convert index to strings for better display
    chart3_data.index = chart3_data.index.map(str)
    
    # Display the chart
    st.line_chart(chart3_data)
    
    # Display 2035 values in a table for Chart 3
    st.write("**Final 2035 Values:**")
    final_values3 = pd.DataFrame({
        'Growth Rate': [f"{int(rate*100)}%" for rate in growth_rates],
        'Combined Total Value (£)': [
            f"£{int(calculate_values(redemption_percentage, rate, vested_shares_input, common_redemption_percentage, total_common_shares, common_purchase_price).loc[2035, 'Combined Total Value']):,}" 
            for rate in growth_rates
        ]
    })
    st.table(final_values3)

except Exception as e:
    st.error(f"An error occurred in the calculation: {str(e)}")
    st.write("Please check your inputs and try again.")

# Add a footer
st.markdown("---")
st.caption("Equity Option Calculator © 2025")
