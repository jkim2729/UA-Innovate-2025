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
from google import genai
from google.genai import types
from collections import Counter

tab2, tab3, tab4, tab5, tab6 = st.tabs(['Transaction History','Balances','Retirement','User Profile','Budget'])
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"  # Or another region where the API is available
MODEL_ID = "your-gemini-model-id"  # Replace with your actual model ID
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_service_account_key.json"

# Plaid API Credentials (Use your own keys from Plaid Dashboard)
PLAID_CLIENT_ID = "67e843b405d1170022eda3f8"
PLAID_SECRET = "3df2ac4f4597c9ba98af368be97696"
PLAID_ENV = plaid.Environment.Sandbox  # Use Sandbox, Development, or Production

# Initialize Plaid API Client
configuration = plaid.Configuration(
    host=PLAID_ENV,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET
    }
)
api_client = plaid.ApiClient(configuration)

if 'client' not in st.session_state:
    
    client = plaid_api.PlaidApi(api_client)
    
    st.session_state['client'] = client

client_name = st.session_state['client']

# Create a sandbox public token
def create_sandbox_token():
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",  
        initial_products=[Products("transactions")],  
    )
    
    response = client_name.sandbox_public_token_create(request)

    return response["public_token"]

# Get a sandbox token
if 'pub_token' not in st.session_state:
    public_token = create_sandbox_token()
    st.session_state['pub_token'] = public_token
else:
    public_token = st.session_state['pub_token']

# Exchange public token for access token


def exchange_sandbox_token(public_token):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response["access_token"]

if 'tokens' not in st.session_state:
    tokens = [exchange_sandbox_token(public_token)]
    st.session_state['tokens'] = tokens
    time.sleep(5)
else:
    tokens = st.session_state['tokens']
def get_transactions(client, user_access_tokens):
    start_date = (datetime.now() - timedelta(days=30)).date()
    end_date = datetime.now().date()

    all_transactions = []

    for token in user_access_tokens:
        try:
            request = TransactionsGetRequest(
                access_token=token,
                start_date=start_date,
                end_date=end_date,
                options={"count": 100}
            )
            response = client.transactions_get(request)
            if response is None:
                st.error("No data returned for transactions.")
            for transaction in response["transactions"]:
                all_transactions.append({
                    "amount": transaction["amount"],
                    "date": transaction["date"],
                    "name": transaction["name"],
                    "merchant_name": transaction.get("merchant_name", "Unknown"),
                    "category": transaction.get("category", ["Uncategorized"])[0]
                })
        except ApiException as e:
            st.error(f"API error: {e}")
            st.error(f"Request body: {request}")


    return pd.DataFrame(all_transactions)

def get_balances(client, user_access_tokens):
    all_balances = []

    for token in user_access_tokens:
        request = AccountsBalanceGetRequest(access_token=token)
        try:
            response = client.accounts_balance_get(request)

            for account in response["accounts"]:
                all_balances.append({
                    "bank_name": account["name"],
                    "available_balance": account["balances"]["available"],
                    "current_balance": account["balances"]["current"],
                    "account_type": account["type"]
                })
        except ApiException as e:
            st.error(f"Error fetching balances: {e}")
    
    return pd.DataFrame(all_balances)
def get_spending_summary(df_transactions):
    # Group transactions by category
    category_totals = df_transactions.groupby("category")["amount"].sum().to_dict()
    
    # Get most frequent spending category
    most_frequent_category = Counter(df_transactions["category"]).most_common(1)[0][0]
    
    summary = {
        "total_spent": df_transactions["amount"].sum(),
        "average_transaction": df_transactions["amount"].mean(),
        "most_frequent_category": most_frequent_category,
        "spending_by_category": category_totals
    }
    
    return summary

def get_financial_advice(spending_summary):
    prompt = f"""
    A user has the following spending pattern:
    - Total Spent: ${spending_summary["total_spent"]:.2f}
    - Average Transaction: ${spending_summary["average_transaction"]:.2f}
    - Most Frequent Category: {spending_summary["most_frequent_category"]}
    - Spending by Category: {spending_summary["spending_by_category"]}
    
    Based on this, suggest a financial literacy module they should take.  
    Choose from: 
    1. Budgeting Basics  
    2. Credit & Debt Management  
    3. Smart Investing  
    4. Savings Strategies  
    5. Understanding Loans & Interest  

    Give a short reason why this module is relevant.
    """

    # Make sure to set your OpenAI API key

    ai_client = genai.Client(api_key='AIzaSyCLsKYp-STratMiisGemdyL-R1sFV_6zQg')

    response = ai_client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Tell me a story in 100 words.',
    config=types.GenerateContentConfig(
        system_instruction='you are a story teller for kids under 5 years old',
        max_output_tokens= 400,
        top_k= 2,
        top_p= 0.5,
        temperature= 0.5,
        response_mime_type= 'application/json',
        stop_sequences= ['\n'],
    ),
    )

    # Get the response content (the financial advice)

    st.write(response.text)
    


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
                try:
                    request = SandboxPublicTokenCreateRequest(
                        institution_id="ins_109508",  # Fake bank for sandbox
                        initial_products=[Products("transactions")]
                    )
                    response = client_name.sandbox_public_token_create(request)
                    public_token = response["public_token"]

                    # Exchange the public token for an access token
                    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
                    exchange_response = client_name.item_public_token_exchange(exchange_request)
                    access_token = exchange_response["access_token"]
                    
                    st.success(f"Bank linked successfully! Access Token: {access_token[:10]}...")  # Show part of the token

                    # Store new bank entry with access_token
                    if bank_name and routing_number and checking_number:
                        bank_entries.append({
                            "bank_name": bank_name,
                            "routing_number": routing_number,
                            "checking_number": checking_number,
                            "plaid_access_token": access_token
                        })

                except Exception as e:
                    st.error(f"Error linking bank: {str(e)}")

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

with tab2:


    # Load Transactions Data
    df_transactions = get_transactions(client_name, tokens)
    st.header("📊 Recent Transactions")
    st.dataframe(df_transactions)

    # Show total spending by category
    st.subheader("💸 Total Spending by Category")
    spending_by_category = df_transactions.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(spending_by_category)

    summary = get_spending_summary(df_transactions)
    advice = get_financial_advice(summary)
    st.write(advice)
with tab3:

    df_balances = get_balances(client_name,tokens)

    st.header("🏦 Account Balances")
    st.dataframe(df_balances)

    # Show total balance across all accounts
    st.subheader("💰 Total Net Balance")
    total_balance = df_balances["current_balance"].sum()
    st.session_state['total_savings'] = total_balance
    st.metric(label="Total Balance", value=f"${total_balance:,.2f}")

with tab4:
    st.title('Retirement!')
    total_balance = st.session_state['total_savings']
    st.write(f'You currently have {total_balance}')


with tab6:
    def get_transaction_history():
        return pd.DataFrame([
            {"date": "2025-03-10", "amount": 150, "category": "Dining"},
            {"date": "2025-03-05", "amount": 60, "category": "Groceries"},
            {"date": "2025-02-12", "amount": 200, "category": "Dining"},
            {"date": "2025-02-08", "amount": 50, "category": "Groceries"},
            {"date": "2025-01-15", "amount": 100, "category": "Entertainment"},
            {"date": "2025-01-10", "amount": 40, "category": "Groceries"},
        ])

    # Load transactions
    df_transactions = get_transaction_history()

    # Convert date column to datetime
    df_transactions['date'] = pd.to_datetime(df_transactions['date'])

    # Extract month and year for comparison
    df_transactions["month"] = df_transactions["date"].dt.to_period("M")

    # Get current and previous month's transactions
    current_month = df_transactions["month"].max()
    previous_month = current_month - 1

    # Group by month and category to calculate total spending
    monthly_spending = df_transactions.groupby(["month", "category"])["amount"].sum().unstack().fillna(0)

    # Get total spending per month
    total_spent_current = monthly_spending.loc[current_month].sum()
    total_spent_previous = monthly_spending.loc[previous_month].sum() if previous_month in monthly_spending.index else 0

    # Calculate savings
    savings = total_spent_previous - total_spent_current
    savings_percent = (savings / total_spent_previous * 100) if total_spent_previous > 0 else 0


    st.subheader("💰 Monthly Spending Comparison")
    st.write(f"**Current Month:** ${total_spent_current:.2f}")
    st.write(f"**Previous Month:** ${total_spent_previous:.2f}")

    if savings > 0:
        st.success(f"🎉 Great job! You saved **${savings:.2f}** ({savings_percent:.2f}% less than last month)!")
    else:
        st.warning(f"🚨 You spent **${-savings:.2f}** more than last month. Let's adjust the budget!")

    # Show spending by category
    st.subheader("📂 Spending Breakdown by Category")
    st.dataframe(monthly_spending)

    # Progress Bar for Savings Goal
    savings_goal = 200  # Example savings goal
    progress = min(savings / savings_goal, 1.0)
    st.subheader("🏆 Savings Progress")
    st.progress(progress)

    if progress >= 1:
        st.balloons()
        st.success("🎉 You've reached your savings goal this month!")

    # Fun Reward System
    if savings > 50:
        st.subheader("🏅 Reward Earned!")
        st.write("You've unlocked the **Smart Saver** badge! Keep it up! 🎖️")

    elif savings > 100:
        st.subheader("💎 Ultimate Saver!")
        st.write("You're a **Budgeting Pro**! Amazing work! 🔥")


