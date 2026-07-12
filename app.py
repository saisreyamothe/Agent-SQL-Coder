"""
Streamlit UI for SQL Coder Agent.
Real-time streaming of agent reasoning.
"""

import streamlit as st
from sql_agent import create_sql_agent_graph, SQLState


st.set_page_config(page_title="SQL Coder Agent", layout="wide")
st.title("🔧 Agentic SQL Coder")
st.markdown("Self-correcting SQL generation with LangGraph")

col1, col2 = st.columns([2, 1])

with col1:
    question = st.text_area(
        "Enter your SQL question:",
        height=100,
        placeholder="e.g., Show all customers who spent over $1000"
    )

with col2:
    st.info("Features:\n✓ Dual-agent\n✓ Max 3 retries\n✓ Real-time feedback")

if st.button("Generate SQL", type="primary"):
    if question:
        st.divider()
        
        agent = create_sql_agent_graph()
        state = SQLState(question=question)
        
        with st.spinner("Agents working..."):
            result = agent.invoke(state)
        
        # Results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Generated SQL")
            st.code(result.final_sql, language="sql")
        
        with col2:
            st.subheader("Developer Reasoning")
            st.info(result.developer_reasoning)
        
        if result.validation_errors:
            st.warning(f"**Validation Issues:** {', '.join(result.validation_errors)}")
        else:
            st.success("✓ SQL validated and ready")
        
        st.caption(f"Retries: {result.retry_count}/3")
