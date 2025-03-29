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
client = plaid_api.PlaidApi(api_client)  #
client_name = client

# Create a sandbox public token
def create_sandbox_token():
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",  
        initial_products=[Products("transactions")],  
    )
    
    response = client_name.sandbox_public_token_create(request)

    return response["public_token"]

# Get a sandbox token
public_token = create_sandbox_token()


# Exchange public token for access token
def exchange_sandbox_token(public_token):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response["access_token"]

tokens = [exchange_sandbox_token(public_token)]
time.sleep(5)
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
                    "account_id": transaction["account_id"],
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




# Streamlit app title
st.title("Personal Finance Dashboard 💰")

# Sidebar Navigation
option = st.sidebar.radio("Select View:", ["Transactions", "Balances"])

# Load Transactions Data
df_transactions = get_transactions(client_name, tokens)

# Display Transactions
if option == "Transactions":
    st.header("📊 Recent Transactions")
    st.dataframe(df_transactions)

    # Show total spending by category
    st.subheader("💸 Total Spending by Category")
    spending_by_category = df_transactions.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(spending_by_category)

# Display Balances
elif option == "Balances":
    st.header("🏦 Account Balances")
