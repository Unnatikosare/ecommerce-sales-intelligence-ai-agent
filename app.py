
import os
import streamlit as st
import mysql.connector
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="E-commerce Sales AI Agent",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ E-commerce Sales Intelligence AI Agent")
st.caption("Ask questions about sales, profit, regions, and products.")

# ---------------- SIDEBAR SETTINGS ----------------

# Load credentials from .streamlit/secrets.toml

groq_api_key = st.secrets["GROQ_API_KEY"]

mysql_config = {
    "host": st.secrets["MYSQL_HOST"],
    "user": st.secrets["MYSQL_USER"],
    "password": st.secrets["MYSQL_PASSWORD"],
    "database": st.secrets["MYSQL_DATABASE"],
}



# ---------------- SQL QUERY ROUTER ----------------
def get_sql_query(question):
    if not isinstance(question, str) or not question.strip():
        return None

    q = question.strip().lower()

    if any(word in q for word in [
        "overall", "summary", "total", "margin"
    ]) and any(word in q for word in [
        "sales", "profit", "business", "margin", "summary"
    ]):
        return """
        SELECT
            ROUND(SUM(Sales), 2) AS Total_Sales,
            ROUND(SUM(Profit), 2) AS Total_Profit,
            ROUND(
                SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2
            ) AS Profit_Margin_Percent
        FROM ecommerce_sales_ai_agent_dataset;
        """

    if any(word in q for word in [
        "region", "regional"
    ]) and any(word in q for word in [
        "sales", "revenue"
    ]):
        return """
        SELECT Region,
               ROUND(SUM(Sales), 2) AS Total_Sales
        FROM ecommerce_sales_ai_agent_dataset
        GROUP BY Region
        ORDER BY Total_Sales DESC;
        """

    if any(word in q for word in [
        "category", "categories"
    ]) and any(word in q for word in [
        "profit", "profitable"
    ]):
        return """
        SELECT Category,
               ROUND(SUM(Profit), 2) AS Total_Profit
        FROM ecommerce_sales_ai_agent_dataset
        GROUP BY Category
        ORDER BY Total_Profit DESC;
        """

    if any(word in q for word in [
        "product", "products", "best-selling"
    ]) and any(word in q for word in [
        "top", "best", "highest", "sales", "selling"
    ]):
        return """
        SELECT Product,
               ROUND(SUM(Sales), 2) AS Total_Sales
        FROM ecommerce_sales_ai_agent_dataset
        GROUP BY Product
        ORDER BY Total_Sales DESC
        LIMIT 10;
        """

    return None


# ---------------- DATABASE + AI ----------------
def answer_question(question):
    query = get_sql_query(question)

    if query is None:
        return (
            "I don't support that question yet. Try asking about "
            "overall business summary, regional sales, category profit, "
            "or top products by sales."
        )

    conn = None

    try:
        conn = mysql.connector.connect(**mysql_config)
        query_check = query.strip().lower()

        if not query_check.startswith("select"):
            return "Only read-only SELECT queries are allowed."

        if any(word in query_check for word in [
        "insert ", "update ", "delete ", "drop ",
        "alter ", "truncate ", "create ", "grant ", "revoke "
         ]):
            return "This query is not allowed."

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return "No results found."

        data = str(rows)

        client = Groq(api_key=groq_api_key)

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an e-commerce data analyst. "
                        "Answer using only the SQL results supplied. "
                        "Report all monetary values in Indian rupees (₹). "
                        "Do not invent facts or make unsupported claims. "
                        "Give a concise answer with key figures."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Business question: {question}\n\n"
                        f"SQL results: {data}"
                    )
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        return (
            f"Could not answer the question. "
            f"Please check your API key and database connection. "
            f"Technical details: {e}"
        )

    finally:
        if conn is not None and conn.is_connected():
            conn.close()


# ---------------- CHAT INTERFACE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested questions
st.markdown("### Try asking")
col1, col2 = st.columns(2)

with col1:
    st.markdown("- Which region has the highest sales?")
    st.markdown("- Which category has the highest profit?")

with col2:
    st.markdown("- Show the top 10 products by sales.")
    st.markdown("- Give me an overall business summary.")


question = st.chat_input("Ask a question about your sales data...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not groq_api_key:
            st.error("Groq API key is missing. Check .streamlit/secrets.toml.")
        else:
            with st.spinner("Analyzing your sales data..."):
                try:
                    answer = answer_question(question)
                    if answer is None:
                        answer = (
                            "I couldn't process that question. Try asking about "
                            "regional sales, category profit, top products, "
                            "or the overall business summary."
                        )
                    st.markdown(str(answer))
                    st.session_state.messages.append(
                        {"role": "assistant", "content": str(answer)}
                    )
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
