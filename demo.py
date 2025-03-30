import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plaid
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model import *
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.plaid_error import PlaidError
from plaid.exceptions import ApiException
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
import time 
import os
from collections import Counter

st.set_page_config(page_title="Dinero Dossier", page_icon="💰", layout="centered")

# Apply custom styles
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
        }
        .login-container {
            max-width: 400px;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .login-title {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
        }
        .btn-login {
            background-color: #2ecc71 !important;
            color: white !important;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Dummy user credentials
USER_CREDENTIALS = {"admin": "password123", "user": "1234"}

# Function to check login
def check_login(username, password):
    return USER_CREDENTIALS.get(username) == password

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login screen
def login():
    st.markdown("<h1 style='text-align: center;'>💰 Dinero Dossier</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Your Smart Financial Advisor</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    
    if st.button("Login", key="login-btn"):
        st.session_state.logged_in = True



    st.markdown("</div>", unsafe_allow_html=True)

def main_app():

    tab2, tab3, tab4, tab5, tab6 = st.tabs(['Transaction History','Balances','Retirement','User Profile','Budget'])

    with tab2:

        df_transactions = pd.read_csv('dummy_data.csv')
        df_transactions.set_index('Unnamed: 0',inplace=True)
        df_transactions["Date"] = pd.to_datetime(df_transactions["Date"])

        # Filter for February transactions
        df_february = df_transactions[df_transactions["Date"].dt.month == 2]
        st.header("📊 Recent Transactions")
        st.dataframe(df_february)

        # Show total spending by category
        st.subheader("💸 Total Spending by Category")
        spending_by_category = df_transactions.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        st.bar_chart(spending_by_category)


        x = st.button('See Personalized Recommended Modules')

        
    with tab3:

        data = {
        "account_id": ["chk_123", "sav_456", "inv_789"],
        "account_type": ["Checking", "Savings", "Investment"],
        "bank_name": ["Bank A", "Bank A", "Investment Firm X"],
        "balance": [1200.50, 5000.75, 15000.30],
        "last_updated": pd.to_datetime(["2025-02-28", "2025-02-28", "2025-02-28"]),
    }
        df_balances = pd.DataFrame(data)
        st.header("🏦 Account Balances")
        st.dataframe(df_balances)
        st.subheader("💰 Total Net Balance")
        total_balance = df_balances["balance"].sum()
        st.session_state['total_savings'] = total_balance
        st.metric(label="Total Balance", value=f"${total_balance:,.2f}")

    with tab5:
        st.title('User Settings!')
        
        # Preloaded user data (for demonstration, replace with actual data fetching)
        existing_data = {
            "name": "John Doe",
            "address": "123 Main St, City, State, ZIP",
            "banks": [
                {"bank_name": "Bank A", "routing_number": "123456789", "checking_number": "987654321", "plaid_access_token": 'PvqnxVdllQtRvBxG5BomSBBDxlQjvVcXagpED'},
                {"bank_name": "Bank B", "routing_number": "987654321", "checking_number": "123456789", "plaid_access_token": 'PvqnxVdllQtRvBxG5BomSBBDxlQjvVcXagpED'},

            ]
        }

        st.subheader("Personal Information")
        st.text_input("Full Name", value=existing_data.get("name", ""), disabled=True)
        address = st.text_area("Address", value=existing_data.get("address", ""))

        st.subheader("Banking Details")
        banks = existing_data.get("banks", [])

        bank_entries = []
        for idx, bank in enumerate(banks):
            with st.expander(f"Bank {idx+1}: {bank['bank_name']}"):
                bank_name = st.text_input(f"Bank Name {idx+1}", value=bank["bank_name"])
                routing_number = st.text_input(f"Routing Number {idx+1}", value=bank["routing_number"])
                checking_number = st.text_input(f"Checking Account Number {idx+1}", value=bank["checking_number"], type="password")
                access_token = bank.get("plaid_access_token", "Not Linked")
                
                bank_entries.append({
                    "bank_name": bank_name,
                    "routing_number": routing_number,
                    "checking_number": checking_number,
                    "plaid_access_token": access_token
                })


        # Adding a new bank
        add_bank = st.checkbox("Add another bank")
        if add_bank:
            with st.expander("New Bank"):
                bank_name = st.text_input("Bank Name (New)")
                routing_number = st.text_input("Routing Number (New)")
                checking_number = st.text_input("Checking Account Number (New)", type="password")
                user_name = st.text_input("Bank Username")
                pass_name = st.text_input('Bank Password')
                # Create a Plaid public token
                if st.button("Link to Plaid"):

                        
                    st.success(f"Bank linked successfully!")


        # Submit updated information
        submitted = st.button("Submit")
        if submitted:
            st.success("Settings Updated Successfully!")
            st.write("### Submitted Information:")
            st.write(f"**Name:** {existing_data.get('name', '')}")
            st.write(f"**Address:** {address}")
            for idx, bank in enumerate(bank_entries):
                st.write(f"**Bank {idx+1}:** {bank['bank_name']}")
                st.write(f"**Routing Number:** {bank['routing_number']}")
                st.write("**Checking Account Number:** [Hidden]")
                st.write(f"**Plaid Access Token:** {bank['plaid_access_token'][:10]}...")  # Partially hide the token for security

    with tab4:
        retirement_data = {
        "account_id": ["ret_001"],
        "account_type": ["Retirement"],
        "balance": [25000.00],  # Current savings
        "monthly_contribution": [1000],  # Monthly deposit
        "expected_growth_rate": [0.06],  # 6% annual return
        "years_until_retirement": [30],  # 30 years to go
    }

        df_retirement = pd.DataFrame(retirement_data)



    # 🏦 Retirement Tab

        st.header("📈 Retirement Planning")

        # Show current savings details
        st.subheader("💰 Current Retirement Savings")
        st.dataframe(df_retirement)

        # Simulate future balance with compound interest formula
        P = df_retirement["balance"][0]  # Initial balance
        r = df_retirement["expected_growth_rate"][0]  # Annual return
        n = 12  # Compounded monthly
        t = df_retirement["years_until_retirement"][0]  # Years left
        monthly_contribution = df_retirement["monthly_contribution"][0]

        # Formula for future value of retirement savings with monthly contributions
        future_balance = P * (1 + r/n) ** (n*t) + monthly_contribution * (((1 + r/n) ** (n*t) - 1) / (r/n))

        st.subheader("📊 Estimated Future Retirement Savings")
        st.write(f"**Projected Balance at Retirement:** ${future_balance:,.2f}")

        # Financial Insights
        st.subheader("💡 Retirement Insights")
        if future_balance < 500000:
            st.warning("You may need to increase your savings rate or retirement contributions.")
        elif 500000 <= future_balance < 1000000:
            st.info("You're on track, but consider maximizing tax-advantaged accounts.")
        else:
            st.success("Great job! You're building a strong retirement fund!")

    with tab6:
        df_transactions['Date'] = pd.to_datetime(df_transactions['Date'])

        # Extract month and year for comparison
        df_transactions["month"] = df_transactions["Date"].dt.to_period("M")
        current_month = df_transactions["month"].max()
        previous_month = current_month - 1

        # Group by month and category to calculate total spending
        monthly_spending = df_transactions.groupby(["month", "Category"])["Amount"].sum().unstack().fillna(0)

        # Get total spending per month
        total_spent_current = monthly_spending.loc[current_month].sum()
        total_spent_previous = monthly_spending.loc[previous_month].sum() if previous_month in monthly_spending.index else 0

        # Calculate savings
        savings = total_spent_previous - total_spent_current
        savings_percent = (savings / total_spent_previous * 100) if total_spent_previous > 0 else 0

        # Streamlit UI for Budget Tab
        st.title("📊 Monthly Budget Overview")

        st.subheader("💰 Monthly Spending Comparison")
        st.write(f"**Current Month:** ${total_spent_current:.2f}")
        st.write(f"**Previous Month:** ${total_spent_previous:.2f}")

        if savings > 0:
            st.success(f"🎉 Great job! You reduced spending by **${savings:.2f}** this month!")
        else:
            st.warning(f"🚨 You spent **${-savings:.2f}** more than last month. Let's adjust the budget!")

        # # Show spending by category
        # st.subheader("📂 Spending Breakdown by Category")
        # st.dataframe(monthly_spending)

        # Progress Bar for Savings Goal
        savings_goal = 200  # Example savings goal
        progress = min(savings / savings_goal, 1.0)
        st.subheader("🏆 Savings Progress")
        st.progress(progress)

        if progress >= 1:
            st.success("🎉 You've reached your savings goal this month!")

        # Fun Reward System
        if savings > 50:
            st.subheader("🏅 Reward Earned!")
            st.write("You've unlocked the **Smart Saver** badge! Keep it up! 🎖️")

        elif savings > 100:
            st.subheader("💎 Ultimate Saver!")
            st.write("You're a **Budgeting Pro**! Amazing work! 🔥")

        st.sidebar.info("Try to improve your savings to earn more rewards! 🚀")

if not st.session_state.logged_in:
    login()
else:
    main_app()