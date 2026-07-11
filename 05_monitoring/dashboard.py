from dataclasses import asdict

import pandas as pd
import streamlit as st
from db_query import get_conversations, get_stats

limit = 50

st.title("Course Assistant Dashboard")

stats = get_stats()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total conversations", stats.total)
col2.metric("Avg response time(s)", f"{stats.avg_response_time:.2f}")
col3.metric("Total cost", f"${stats.total_cost:.4f}")
col4.metric("Avg tokens", f"{stats.avg_tokens:.0f}")

# charts for cost and response time over time
records = get_conversations(limit=limit)
df = pd.DataFrame([asdict(r) for r in records])

st.subheader(f"Cost for the last {limit} conversations")
st.scatter_chart(df, x="timestamp", y="cost")

st.subheader(f"Response time for the last {limit} conversations")
st.scatter_chart(df, x="timestamp", y="response_time")


# recent conversations
st.subheader("Top 10 most recent conversations")
records = get_conversations(limit=10)

for record in records:
    st.write(f"**{record.prompt[:80]}...**")
    st.write(f"{record.answer[:200]}...")
    st.write(f"Time: {record.response_time:.2f}s | Cost: ${record.cost:.4f}")
    st.divider()
