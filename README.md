# 🛍️ E-commerce Sales Intelligence AI Agent

A data analytics project that helps users explore e-commerce sales, profit, regional performance, and top-selling products through an interactive Streamlit chat interface.

## 🚀 Live Demo

[**Open the Live App**](https://ecommerce-sales-intelligence-ai-agent-dm6aatfhahzhoqtbbb7jw2.streamlit.app/)

## ✨ Features

- Analyze overall sales, profit, and profit margin.
- Compare sales performance across regions.
- Identify the most profitable product categories.
- View the top 10 products by sales.
- Ask business questions through an interactive chat interface.
- Calculate results directly from a CSV dataset.
- Optional Groq API integration for AI-generated summaries.

## 🧰 Tech Stack

- Python
- Pandas
- Streamlit
- Groq API (optional)
- Git and GitHub

## 📊 Key Business Metrics

The current dataset analysis reports:

- **Total Sales:** ₹4,30,05,656.85
- **Total Profit:** ₹78,72,564.20
- **Total Orders:** 2,500
- **Profit Margin:** 18.31%

These figures are calculated from the dataset used by the deployed demo.

## 💬 Example Questions

- Which region has the highest sales?
- Which category has the highest profit?
- Show the top 10 products by sales.
- Give me an overall business summary.

## ▶️ Run Locally

1. Clone this repository.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Run the app:

   `streamlit run app.py`

## 🔐 Configuration

The CSV-based demo can calculate results without a MySQL connection. To enable Groq-generated summaries, configure `GROQ_API_KEY` in Streamlit Secrets. Never commit API keys or passwords to GitHub.

## 👩‍💻 Author

**Unnati Kosare**

[GitHub Profile](https://github.com/Unnatikosare)
