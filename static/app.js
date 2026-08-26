"use strict";

const categories = ["Food & Dining", "Travel", "Salary", "Miscellaneous"];
const categoryColors = {
	"Food & Dining": "#dc765f",
	Travel: "#5a83a6",
	Salary: "#25734a",
	Miscellaneous: "#e8ae48",
};

const formatCurrency = (amount) => new Intl.NumberFormat("en-IN", {
	style: "currency",
	currency: "INR",
	maximumFractionDigits: 2,
}).format(amount);

function renderSummary(summary) {
	document.querySelector("#total-income").textContent = formatCurrency(summary.total_income);
	document.querySelector("#total-expenses").textContent = formatCurrency(summary.total_expenses);
	document.querySelector("#transaction-count").textContent = summary.transaction_count;

	document.querySelector("#category-cards").innerHTML = categories.map((category) => `
		<article class="category-card" style="--category-color: ${categoryColors[category]}">
			<div class="category-top"><span class="category-name">${category}</span><span class="category-value">${formatCurrency(summary[category])}</span></div>
			<div class="progress-track"><div class="progress-bar" style="width: ${summary.category_progress[category]}%"></div></div>
		</article>
	`).join("");
}

function renderTransactions(transactions) {
	const feed = document.querySelector("#transaction-feed");
	feed.innerHTML = transactions.map((transaction) => {
		const amountClass = transaction.amount >= 0 ? "income" : "expense";
		const amountPrefix = transaction.amount >= 0 ? "+" : "-";
		const absoluteAmount = Math.abs(transaction.amount);
		const savings = transaction.expected_savings === null ? "" : `
			<div class="savings">🟢 Expected Savings<br>${formatCurrency(transaction.expected_savings)} projected reward</div>
		`;
		const options = categories.map((category) => `<option value="${category}" ${category === transaction.category ? "selected" : ""}>${category}</option>`).join("");
		return `
			<article class="transaction-row">
				<div><div class="transaction-description">${transaction.raw_message}</div><div class="transaction-type">${new Date(transaction.timestamp).toLocaleString()}</div>${savings}</div>
				<div class="transaction-amount ${amountClass}">${amountPrefix}${formatCurrency(absoluteAmount)}</div>
				<select class="category-select" data-transaction-id="${transaction.id}" aria-label="Category for ${transaction.merchant}">${options}</select>
			</article>
		`;
	}).join("");
	document.querySelector("#feed-status").textContent = `${transactions.length} transactions`;
}

async function loadDashboard() {
	const [transactionsResponse, summaryResponse] = await Promise.all([
		fetch("/api/transactions"),
		fetch("/api/summary"),
	]);
	if (!transactionsResponse.ok || !summaryResponse.ok) throw new Error("Dashboard data could not be loaded");
	renderTransactions(await transactionsResponse.json());
	renderSummary(await summaryResponse.json());
}

document.querySelector("#transaction-feed").addEventListener("change", async (event) => {
	if (!event.target.matches(".category-select")) return;
	const transactionId = event.target.dataset.transactionId;
	const response = await fetch(`/api/transactions/${transactionId}/category`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ category: event.target.value }),
	});
	if (!response.ok) {
		await loadDashboard();
		return;
	}
	await loadDashboard();
});

document.querySelector("#message-form").addEventListener("submit", async (event) => {
	event.preventDefault();
	const form = event.currentTarget;
	const input = form.querySelector("#message-input");
	const button = form.querySelector("button");
	const status = document.querySelector("#form-status");
	button.disabled = true;
	status.textContent = "";

	try {
		const response = await fetch("/api/transactions", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ message: input.value }),
		});
		const result = await response.json();
		if (!response.ok) throw new Error(result.error || "Transaction could not be added");
		input.value = "";
		status.textContent = "Transaction added";
		await loadDashboard();
	} catch (error) {
		status.textContent = error.message;
	} finally {
		button.disabled = false;
	}
});

loadDashboard().catch(() => {
	document.querySelector("#feed-status").textContent = "Unable to load activity";
});
