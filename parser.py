import re


CATEGORIES = ("Food & Dining", "Travel", "Salary", "Miscellaneous")

SAMPLE_MESSAGES = [
	"Paid Rs. 250 to Zomato via UPI",
	"Paid Rs. 450 to Swiggy via UPI",
	"Paid Rs. 320 to Uber via UPI",
	"Received Rs. 50,000 from Private Company Ltd",
	"Paid Rs. 800 to Amazon Cashback",
	"Paid Rs. 650 at Local Store",
]

CATEGORY_KEYWORDS = {
	"Food & Dining": ("zomato", "swiggy", "restaurant", "cafe", "food"),
	"Travel": ("uber", "ola", "rapido", "metro", "irctc", "flight"),
	"Salary": ("salary", "payroll", "company", "employer"),
}

REWARD_KEYWORDS = (
	"cashback",
	"reward",
	"rewards",
	"cashkaro",
	"cred",
	"phonepe rewards",
	"paytm rewards",
)

SAMPLE_TIMESTAMPS = (
	"2026-08-26T20:30:00",
	"2026-08-26T19:45:00",
	"2026-08-26T18:20:00",
	"2026-08-26T17:00:00",
	"2026-08-26T16:15:00",
	"2026-08-26T15:30:00",
)


def _extract_amount(message):
	match = re.search(r"(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d{1,2})?)", message, re.IGNORECASE)
	if not match:
		raise ValueError("Transaction message does not contain a valid amount")
	return float(match.group(1).replace(",", ""))


def _extract_merchant(message):
	match = re.search(r"\b(?:to|at|from)\s+(.+?)(?:\s+via\s+upi)?$", message, re.IGNORECASE)
	if not match:
		raise ValueError("Transaction message does not contain a merchant or sender")
	return match.group(1).strip()


def _get_category(message):
	normalized_message = message.casefold()
	for category, keywords in CATEGORY_KEYWORDS.items():
		if any(keyword in normalized_message for keyword in keywords):
			return category
	return "Miscellaneous"


def parse_transaction(message):
	"""Parse one raw UPI message into normalized transaction data."""
	amount = _extract_amount(message)
	is_income = bool(re.search(r"\b(received|credited|income)\b", message, re.IGNORECASE))
	merchant = _extract_merchant(message)
	has_expected_savings = (
		not is_income
		and any(keyword in message.casefold() for keyword in REWARD_KEYWORDS)
	)

	return {
		"raw_message": message,
		"merchant": merchant,
		"amount": amount if is_income else -amount,
		"transaction_type": "income" if is_income else "expense",
		"category": _get_category(message),
		"expected_savings": round(amount * 0.05, 2) if has_expected_savings else None,
	}


def parse_sample_transactions():
	return [
		{**parse_transaction(message), "timestamp": timestamp}
		for message, timestamp in zip(SAMPLE_MESSAGES, SAMPLE_TIMESTAMPS)
	]


def aggregate_summary(transactions):
	"""Reduce parsed transactions into dashboard summary values."""
	summary = {
		"total_income": 0.0,
		"total_expenses": 0.0,
		"Food & Dining": 0.0,
		"Travel": 0.0,
		"Salary": 0.0,
		"Miscellaneous": 0.0,
		"transaction_count": len(transactions),
		"category_progress": {category: 0.0 for category in CATEGORIES},
	}

	for transaction in transactions:
		amount = transaction["amount"]
		if amount >= 0:
			summary["total_income"] += amount
		else:
			summary["total_expenses"] += abs(amount)
		summary[transaction["category"]] += abs(amount)

	total_category_value = sum(summary[category] for category in CATEGORIES)
	if total_category_value:
		for category in CATEGORIES[:-1]:
			summary["category_progress"][category] = round(
				summary[category] / total_category_value * 100,
				2,
			)
		last_category = CATEGORIES[-1]
		summary["category_progress"][last_category] = round(
			100 - sum(summary["category_progress"].values()),
			2,
		)

	return summary
