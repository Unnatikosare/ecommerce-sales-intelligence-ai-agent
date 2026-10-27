# E-commerce Sales Intelligence AI Agent

An AI-powered sales analytics application that helps users explore e-commerce performance through natural-language questions.

## Features
- Interactive Streamlit chat interface
- Sales and profit analysis by region and category
- Top 10 products by sales
- Overall business summary
- Groq API integration for AI-generated insights
- MySQL database integration for analytics queries

## Tech Stack
- Python
- Pandas
- MySQL
- Groq API
- Streamlit

## Setup

1. Clone or download this repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml` locally with your own credentials:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   MYSQL_HOST = "localhost"
   MYSQL_USER = "your-mysql-user"
   MYSQL_PASSWORD = "your-mysql-password"
   MYSQL_DATABASE = "ecommerce_ai"
   ```

4. Make sure your MySQL database and `ecommerce_sales_ai_agent_dataset` table are set up.
5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Security
- Never commit API keys, passwords, or `.streamlit/secrets.toml`.
- Use a dedicated read-only database user when deploying.

## Project Status
Local prototype tested with sample sales, category-profit, top-product, and business-summary questions.