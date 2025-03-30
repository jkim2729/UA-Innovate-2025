import pandas as pd
import random
from datetime import datetime, timedelta

# Define categories and merchants
categories = {
    "Groceries": ["Walmart", "Whole Foods", "Kroger", "Safeway", "Trader Joe's"],
    "Dining": ["McDonald's", "Starbucks", "Subway", "Chipotle", "Olive Garden"],
    "Transportation": ["Uber", "Lyft", "Shell", "ExxonMobil", "BP"],
    "Shopping": ["Amazon", "Target", "Best Buy", "Apple Store", "Nike"],
    "Entertainment": ["BET365",'Draftkings','Fanduel'],
    "Utilities": ["AT&T", "Verizon", "Comcast", "Duke Energy", "PG&E"],
    "Debt": ["Car","Discover","Mastercard"]
}

# Generate random transactions
def generate_transactions(start_date, end_date, num_transactions=50):
    transactions = []
    current_date = start_date
    while current_date <= end_date:
        for _ in range(random.randint(1, 3)):  # 1-3 transactions per day
            category = random.choice(list(categories.keys()))
            merchant = random.choice(categories[category])
            amount = round(random.uniform(5, 200), 2)  # Random amount between $5 and $200
            transactions.append([amount, current_date.strftime("%Y-%m-%d"), "John Doe", merchant, category])
        current_date += timedelta(days=1)
    return transactions

# Define date ranges for the requested months
date_ranges = [
    (datetime(2024, 1, 1), datetime(2024, 1, 31)),
    (datetime(2025, 1, 1), datetime(2025, 1, 31)),
    (datetime(2025, 2, 1), datetime(2025, 2, 28))
]

# Generate data
all_transactions = []
for start_date, end_date in date_ranges:
    all_transactions.extend(generate_transactions(start_date, end_date))

# Create DataFrame
df = pd.DataFrame(all_transactions, columns=["Amount", "Date", "Name", "Merchant Name", "Category"])
df.to_csv('dummy_data.csv')