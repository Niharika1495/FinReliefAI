NEGOTIATION_STRATEGY_PROMPT = """You are a professional financial negotiation adviser.
Analyze the following details to generate a comprehensive debt negotiation strategy:
Borrower: {name}
Lender: {lender_name}
Loan Type: {loan_type}
Outstanding Balance: ${outstanding_amount:,.2f}
Interest Rate: {interest_rate}%
Missed Payments / Overdue Months: {overdue_months}
Recommended Settlement Offer: ${recommended_amount:,.2f} ({settlement_percentage}% of balance)
Estimated Savings: ${estimated_savings:,.2f}
Negotiation Difficulty: {negotiation_difficulty}
User Hardship Profile: {hardship_description}

Provide:
1. A professional negotiation strategy overview.
2. Sequential negotiation steps.
3. Key talking points for calls.
4. Best settlement approach.
5. Expected lender concerns and recommended responses.

Format the output clearly and professionally using markdown. Do not perform any new financial calculations.
"""

SETTLEMENT_LETTER_PROMPT = """Write a formal debt settlement proposal letter.
Use a professional business letter format.
Details:
Borrower Name: {name}
Lender Name: {lender_name}
Loan Type: {loan_type}
Outstanding Balance: ${outstanding_amount:,.2f}
Monthly Installment (EMI): ${emi:,.2f}
Overdue Months: {overdue_months}
Settlement Offer: ${recommended_amount:,.2f} ({settlement_percentage}% of balance)
Borrower Hardship: {hardship_description}

The letter must address the lender, state the financial hardship clearly, propose the settlement amount of ${recommended_amount:,.2f} as a single payment or installment option, justify why this is the maximum possible payment, and close professionally. Do not include placeholders; write complete text. Do not perform any new financial calculations.
"""

NEGOTIATION_EMAIL_PROMPT = """Write a professional email proposal to the creditor requesting debt settlement.
Details:
Lender Name: {lender_name}
Loan Type: {loan_type}
Outstanding Balance: ${outstanding_amount:,.2f}
Proposed Settlement: ${recommended_amount:,.2f} ({settlement_percentage}% of balance)
Borrower Hardship: {hardship_description}
Borrower Name: {name}

Generate:
Subject line and email body. Keep it concise, professional, and clear. Propose the settlement amount of ${recommended_amount:,.2f} and outline the hardship. Closing should be professional. Provide output strictly in this format:
Subject: [Subject Line]
---
[Email Body]
"""

FINANCIAL_EXPLANATION_PROMPT = """Explain the user's financial health analysis in plain English.
Details:
Monthly Income: ${monthly_income:,.2f}
Monthly Expenses: ${monthly_expenses:,.2f}
Monthly Surplus: ${monthly_surplus:,.2f}
Debt-to-Income (DTI) Ratio: {dti_ratio}%
EMI-to-Income Ratio: {emi_ratio}%
Financial Health Score: {financial_health_score}/100
Risk Level: {risk_level}
Repayment Capacity: {repayment_capacity}
Rule-Based Recommendations:
{recommendations}

Explain what these metrics mean for the user, how the score was calculated (briefly), why their risk level is {risk_level}, and how they should prioritize their budget and debt payoff based on these results. Keep it supportive, clear, and actionable. Do not perform any new financial calculations.
"""
