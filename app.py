from flask import Flask, jsonify, render_template, request

from parser import CATEGORIES, aggregate_summary, parse_sample_transactions

app = Flask(__name__)
transactions = [
    {"id": index, **transaction}
    for index, transaction in enumerate(parse_sample_transactions(), start=1)
]
transactions.sort(key=lambda transaction: transaction["timestamp"], reverse=True)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/summary")
def summary():
    return jsonify(aggregate_summary(transactions))


@app.get("/api/transactions")
def get_transactions():
    return jsonify(transactions)


@app.patch("/api/transactions/<int:transaction_id>/category")
def update_category(transaction_id):
    transaction = next(
        (item for item in transactions if item["id"] == transaction_id),
        None,
    )
    if transaction is None:
        return jsonify({"error": "Transaction not found"}), 404

    data = request.get_json(silent=True) or {}
    category = data.get("category")
    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    transaction["category"] = category
    return jsonify(transaction)


if __name__ == "__main__":
    app.run(debug=True)
