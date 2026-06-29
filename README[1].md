# Agentic SQL Coder — Self-Correcting LangGraph Pipeline

**Zero Hallucinations** | **Max 3 Retries** | **Real-time Streaming** | **Production Ready**

Multi-agent SQL generation system with self-correction using LangGraph, OpenAI Function Calling, and AgentState for robust database query creation.

## Key Features

- **Dual-Agent Architecture**: Senior SQL Developer + SQL QA Engineer roles
- **Self-Correction Loop**: Automatic retry with feedback, max 3 attempts
- **Real-time Streaming**: Stream reasoning via Streamlit
- **Production Observability**: Full node-by-node logging

## Architecture

```
User Query
    ↓
[SQL Developer Agent] → Generate SQL with reasoning
    ↓
[QA Engineer Agent] → Validate & provide feedback
    ↓
Retry Loop (max 3) → If failed, loop back with errors
    ↓
Final SQL Query
```

## Installation

```bash
git clone https://github.com/yourusername/LangGraph-SQL-Coder.git
cd LangGraph-SQL-Coder

pip install -r requirements.txt
```

## Quick Start

```python
from src.sql_agent import SQLCoderAgent

agent = SQLCoderAgent(
    database_url="postgresql://user:pass@localhost/db",
    model="gpt-4"
)

result = agent.generate_sql(
    question="Show me all customers who spent over $1000 last month"
)

print(result['sql'])  # Final SQL
print(result['reasoning'])  # Agent reasoning
```

## Usage

```bash
streamlit run src/app.py
```

Visit `http://localhost:8501` for interactive UI with streaming responses.

## License

MIT License
