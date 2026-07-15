"""
Self-correcting SQL generation using LangGraph.
Dual-agent: SQL Developer + QA Engineer
Max 3 retries with feedback loop.
"""

from langgraph.graph import StateGraph, END
from langchain.llms import OpenAI
from pydantic import BaseModel, Field
from typing import List
import json


class SQLState(BaseModel):
    """Agent state for SQL generation."""
    question: str
    sql_draft: str = ""
    validation_errors: List[str] = Field(default_factory=list)
    developer_reasoning: str = ""
    qa_feedback: str = ""
    retry_count: int = 0
    final_sql: str = ""


class SQLDeveloperAgent:
    """Senior SQL Developer role - generates SQL."""
    
    def __init__(self):
        self.llm = OpenAI(model_name="gpt-4")
    
    def generate_sql(self, question: str, feedback: str = "") -> tuple:
        """Generate SQL with developer reasoning."""
        prompt = f"""You are a senior SQL developer. Generate SQL for this question:
        
Question: {question}

{f"Previous attempt feedback: {feedback}" if feedback else ""}

Provide:
1. SQL query
2. Your reasoning

Format as JSON with keys: "sql", "reasoning"
"""
        
        response = self.llm(prompt)
        data = json.loads(response)
        
        return data["sql"], data["reasoning"]


class SQLQAEngineer:
    """SQL QA Engineer - validates and provides feedback."""
    
    def __init__(self):
        self.llm = OpenAI(model_name="gpt-4")
    
    def validate(self, sql: str, question: str) -> tuple:
        """Validate SQL and return feedback."""
        prompt = f"""As SQL QA engineer, validate this SQL:

SQL: {sql}
Question: {question}

Check:
1. Syntax correctness
2. Logic correctness  
3. Does it answer the question?

Format as JSON: {{"valid": bool, "errors": [str], "suggestions": [str]}}
"""
        
        response = self.llm(prompt)
        data = json.loads(response)
        
        return data["valid"], data.get("errors", []), data.get("suggestions", [])


def developer_node(state: SQLState) -> SQLState:
    """SQL Developer generates SQL."""
    dev = SQLDeveloperAgent()
    sql, reasoning = dev.generate_sql(
        state.question,
        state.qa_feedback if state.retry_count > 0 else ""
    )
    
    state.sql_draft = sql
    state.developer_reasoning = reasoning
    return state


def qa_node(state: SQLState) -> SQLState:
    """QA Engineer validates SQL."""
    qa = SQLQAEngineer()
    valid, errors, suggestions = qa.validate(state.sql_draft, state.question)
    
    if valid:
        state.final_sql = state.sql_draft
        state.qa_feedback = "✓ SQL is valid and ready"
    else:
        state.validation_errors = errors
        state.qa_feedback = f"Issues: {', '.join(errors)}. Suggestions: {', '.join(suggestions)}"
    
    return state


def should_continue(state: SQLState) -> str:
    """Decide: end or retry."""
    if state.final_sql:
        return END
    
    state.retry_count += 1
    if state.retry_count >= 3:
        return END
    
    return "developer"


def create_sql_agent_graph():
    """Create LangGraph agent."""
    workflow = StateGraph(SQLState)
    
    workflow.add_node("developer", developer_node)
    workflow.add_node("qa", qa_node)
    
    workflow.set_entry_point("developer")
    workflow.add_edge("developer", "qa")
    workflow.add_conditional_edges(
        "qa",
        should_continue,
        {"developer": "developer", END: END}
    )
    
    return workflow.compile()


if __name__ == "__main__":
    agent = create_sql_agent_graph()
    state = SQLState(question="Show customers with orders over $1000")
    result = agent.invoke(state)
    
    print(f"Final SQL:\n{result.final_sql}")
    print(f"Retries: {result.retry_count}")
