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
    data = pd.read_csv("ecommerce_sales_ai_agent_dataset.csv")
    data.columns = data.columns.str.strip()
    for col in ["Sales", "Profit"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

st.success(f"Dataset loaded: {len(df):,} rows")


def get_results(question):
    q = question.lower().strip()

    if any(word in q for word in ["summary", "overall", "total business"]):
        total_sales = float(df["Sales"].sum())
        total_profit = float(df["Profit"].sum())
        return "summary", {
            "Total Sales (₹)": round(total_sales, 2),
            "Total Profit (₹)": round(total_profit, 2),
            "Total Orders": int(df["Order_ID"].nunique()),
            "Profit Margin (%)": round(total_profit / total_sales * 100, 2) if total_sales else 0,
        }

    if "region" in q and any(word in q for word in ["sales", "revenue", "highest"]):
        values = df.groupby("Region", dropna=False)["Sales"].sum().sort_values(ascending=False).round(2)
        return "region", {"Region": values.index.tolist(), "Sales (₹)": values.values.tolist()}

    if "category" in q and "profit" in q:
        values = df.groupby("Category", dropna=False)["Profit"].sum().sort_values(ascending=False).round(2)
        return "category", {"Category": values.index.tolist(), "Profit (₹)": values.values.tolist()}

    if "product" in q and any(word in q for word in ["top", "best", "sales", "selling"]):
        values = df.groupby("Product", dropna=False)["Sales"].sum().sort_values(ascending=False).head(10).round(2)
        return "products", {"Product": values.index.tolist(), "Sales (₹)": values.values.tolist()}

    return None, None


def money(value):
    return f"₹{value:,.2f}"


def display_answer(question, kind, result):
    if kind in ("region", "category", "products"):
        label = "Region" if kind == "region" else ("Category" if kind == "category" else "Product")
        metric = "Sales (₹)" if kind in ("region", "products") else "Profit (₹)"
        table = pd.DataFrame({label: result[label], metric: result[metric]})
        table[metric] = table[metric].map(money)
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config={
                label: st.column_config.TextColumn(label, width="medium"),
                metric: st.column_config.TextColumn(metric, width="medium"),
            },
        )
        if kind == "region" and len(table):
            st.markdown(f"**{table.iloc[0]['Region']} has the highest sales: {table.iloc[0]['Sales (₹)']}**")
        elif kind == "category" and len(table):
            st.markdown(f"**{table.iloc[0]['Category']} has the highest profit: {table.iloc[0]['Profit (₹)']}**")
        return table.to_dict(orient="records")

    table = pd.DataFrame(
        [{"Metric": key, "Value": (money(value) if "(₹)" in key else value)} for key, value in result.items()]
    )
    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="medium"),
        },
    )
    return table.to_dict(orient="records")


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
                kind, result = get_results(question)
                if kind is None:
                    answer = "Try asking about overall business summary, regional sales, category profit, or top products by sales."
                    st.markdown(answer)
                else:
                    display_result = display_answer(question, kind, result)
                    api_key = st.secrets.get("GROQ_API_KEY", "")
                    if api_key:
                        client = Groq(api_key=api_key)
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are an e-commerce data analyst. Answer only from the supplied results. "
                                        "Use Indian rupees for monetary values. Be concise and do not invent facts."
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content": f"Question: {question}\nResults: {display_result}",
                                },
                            ],
                            temperature=0.2,
                        )
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                    else:
                        answer = "Results are calculated directly from the dataset. Add GROQ_API_KEY in Streamlit Secrets to enable AI-generated summaries."
                        st.caption(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
