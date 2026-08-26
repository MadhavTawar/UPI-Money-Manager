# UPI Money Manager

A simple full-stack dashboard for understanding sample UPI activity. The Flask backend parses raw payment messages, calculates summaries and projected cashback, and serves a lightweight vanilla JavaScript frontend.

## Features

- Parses sample UPI payment and receipt messages in chronological order
- Detects income and expenses with signed amounts
- Categorizes transactions into Food & Dining, Travel, Salary, or Miscellaneous
- Shows income, expenses, category totals, and transaction count
- Displays projected savings for qualifying cashback transactions
- Allows category updates from the dashboard
- Accepts new raw transaction alerts directly from the dashboard

## Tech Stack

- Python 3
- Flask
- HTML and CSS
- Vanilla JavaScript
- In-memory sample data; no database or authentication

## Architecture

`parser.py` owns message parsing, categorization, timestamps, expected savings, and aggregation. `app.py` owns Flask routes and the in-memory transaction list. `templates/index.html`, `static/style.css`, and `static/app.js` provide the dashboard presentation and API interactions.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app run
```

Open <http://127.0.0.1:5000> in a browser.

## API Endpoints

- `GET /` - Dashboard frontend
- `GET /api/transactions` - Parsed in-memory transactions
- `POST /api/transactions` - Parse and add a transaction with `{ "message": "Paid Rs. 100 to Cafe" }`
- `GET /api/summary` - Income, expense, category, and count totals
- `PATCH /api/transactions/<id>/category` - Update a category with `{ "category": "Travel" }`

The PATCH endpoint accepts only `Food & Dining`, `Travel`, `Salary`, and `Miscellaneous`. Invalid categories return `400`; unknown transaction IDs return `404`.

## Categorization Logic

Matching is case-insensitive. Food & Dining recognizes Zomato, Swiggy, restaurant, cafe, and food. Travel recognizes Uber, Ola, Rapido, Metro, IRCTC, and flight. Salary recognizes salary, payroll, company, and employer. Unmatched messages become Miscellaneous. Reward terms include Cashback, reward, rewards, CashKaro, CRED, PhonePe Rewards, and Paytm Rewards.

## Expected Savings Logic

For outbound transactions whose message contains `Cashback`, `reward`, or `rewards`, the backend returns `5%` of the original transaction amount as `expected_savings`. All other transactions return `null`. The frontend only displays this backend value.
