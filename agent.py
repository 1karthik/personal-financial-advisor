import os
from dotenv import load_dotenv
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
import requests
import pandas as pd
import fitz  # PyMuPDF

# Load environment variables from .env file
load_dotenv()

def get_stock_price(*args, **kwargs):
    """Get the current stock price for a given symbol."""
    symbol = args[0] if args else kwargs.get('symbol', '')
    symbol = symbol.upper()
    
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        dummy = {"AAPL": 175.2, "GOOG": 130.5, "TSLA": 700.1}
        price = dummy.get(symbol)
        return (
            f"The current price of {symbol} is ${price} (demo)."
            if price
            else f"No data for {symbol}."
        )
    
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    )
    try:
        data = requests.get(url, timeout=10).json()
        price = data["Global Quote"]["05. price"]
        return f"The current price of {symbol} is ${price}."
    except Exception:
        return f"Couldn't fetch price for {symbol} right now."

def explain_concept(*args, **kwargs):
    """Explains financial concepts in simple terms."""
    query = args[0] if args else kwargs.get('query', '')
    mapping = {
        "compound interest": "Compound interest is interest on both principal and accumulated interest.",
        "diversification": "Diversification mixes different investments to reduce risk.",
    }
    for key, desc in mapping.items():
        if key in query.lower():
            return desc
    return "No explanation available."


def safe_eval_math(*args, **kwargs):
    """Evaluate math using python builtin functions."""
    query = args[0] if args else kwargs.get('query', '')
    try:
        result = eval(query, {"__builtins__": {}}, {})
        return f"The result is {result}."
    except Exception:
        return "Invalid math expression."

def read_csv_summary(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path)
        summary = f"Columns: {', '.join(df.columns)}\n"
        summary += f"Rows: {len(df)}\n"
        summary += f"Sample:\n{df.head(3).to_string(index=False)}"
        return summary
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

def read_pdf_text(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text[:2000]  # Limit length
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# List of tools available to the agent
tools = [
    Tool(name="Stock Price", func=get_stock_price, description="Get the current stock price for a given symbol."),
    Tool(name="Concept Explainer", func=explain_concept, description="Get the basic definition of a financial concept."),
    Tool(name="Calculator", func=safe_eval_math, description="Useful for performing mathematical calculations."),
    Tool(name="CSV Reader", func=read_csv_summary, description="Reads financial data from a CSV file. Input should be the file path."),
    Tool(name="PDF Reader", func=read_pdf_text, description="Reads financial text from a PDF file. Input should be the file path."),
    Tool(name="Final Answer", func=lambda x: x, description="Use this to give your final answer to the user."),
]

# Create a simple prompt template
prompt = PromptTemplate.from_template("""You are a helpful financial advisor that can use tools to answer questions.

Question: {input}

Available tools:
{tools}

Available tool names: [{tool_names}]

You must follow this EXACT format:
Thought: (your reasoning)
Action: (tool name from [{tool_names}])
Action Input: (input for the tool)
Observation: (tool's response)
Thought: (your next reasoning)
Action: Final Answer
Action Input: (your detailed explanation)

Example for concept explanation:
Question: What is compound interest?
Thought: I need to get the basic definition of compound interest first
Action: Concept Explainer
Action Input: compound interest
Observation: Compound interest is interest on both principal and accumulated interest.
Thought: Now I can explain the concept in detail
Action: Final Answer
Action Input: Compound interest is a powerful financial concept where you earn interest not just on your initial investment, but also on the accumulated interest. For example, if you invest $1000 at 5% interest, after one year you'll have $1050. In the second year, you'll earn interest on $1050, not just the original $1000. This creates a snowball effect that can significantly grow your wealth over time.

{agent_scratchpad}

Begin!

Thought:""")

# Initialize LlamaCpp model
llm = LlamaCpp(
    model_path="C:\\Users\\karth\\models\\mistral-7b-instruct-v0.1.Q4_0.gguf",
    n_ctx=2048,
    n_gpu_layers=20,
    temperature=0.3,
    max_tokens=1024,
    verbose=True,
)

# Create the ReAct agent using the create_react_agent function
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

# Create an agent executor from the agent and tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
    return_intermediate_steps=True
)
