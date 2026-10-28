
import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(
    page_title="E-commerce Sales AI Agent",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ E-commerce Sales Intelligence AI Agent")
st.caption("Ask questions about sales, profit, regions, and products.")

@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce_sales_ai_agent_dataset.csv")
    df.columns = df.columns.str.strip()
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

st.success(f"Dataset loaded: {len(df):,} rows")

def answer_question(question):
    q = question.lower()

    if any(word in q for word in ["summary", "overall", "total business"]):
        result = {
            "Total Sales": round(df["Sales"].sum(), 2),
            "Total Profit": round(df["Profit"].sum(), 2),
            "Total Orders": int(df["Order_ID"].nunique()),
            "Profit Margin (%)": round(
                df["Profit"].sum() / df["Sales"].sum() * 100, 2
            ) if df["Sales"].sum() else 0
        }

    elif "region" in q and any(word in q for word in ["sales", "revenue", "highest"]):
        result = (
            df.groupby("Region", dropna=False)["Sales"]
            .sum().sort_values(ascending=False).round(2).to_dict()
        )

    elif "category" in q and "profit" in q:
        result = (
            df.groupby("Category", dropna=False)["Profit"]
            .sum().sort_values(ascending=False).round(2).to_dict()
        )

    elif "product" in q and any(word in q for word in ["top", "best", "sales", "selling"]):
        result = (
            df.groupby("Product", dropna=False)["Sales"]
            .sum().sort_values(ascending=False).head(10).round(2).to_dict()
        )

    else:
        return "Try asking about overall business summary, regional sales, category profit, or top products by sales."

    st.dataframe(
        pd.DataFrame(list(result.items()), columns=["Metric", "Value"]),
        use_container_width=True,
        hide_index=True
    )

    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return f"Here are the results from your dataset:\n\n{result}"

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an e-commerce data analyst. "
                    "Answer only from the supplied results. "
                    "Use Indian rupees (₹) for monetary values. "
                    "Be concise and do not invent facts."
                )
            },
            {
                "role": "user",
                "content": f"Question: {question}\nResults: {result}"
            }
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown("### Try asking")
st.markdown(
    "- Which region has the highest sales?\n"
    "- Which category has the highest profit?\n"
    "- Show the top 10 products by sales.\n"
    "- Give me an overall business summary."
)

question = st.chat_input("Ask a question about your sales data...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your sales data..."):
            try:
                answer = answer_question(question)
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
