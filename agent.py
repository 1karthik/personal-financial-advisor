from dotenv import load_dotenv
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()


# Define a very simple tool function that returns the current time
def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime  # Import datetime module to get current time

    now = datetime.datetime.now()  # Get current time
    return now.strftime("%I:%M %p")  # Format time in H:MM AM/PM format

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

# List of tools available to the agent
tools = [
    Tool(
        name="Time",  # Name of the tool
        func=get_current_time,  # Function that the tool will execute
        description="Useful for when you need to know the current time",
    ),
    Tool(
        name="Concept Explainer",
        func=explain_concept,
        description="Explain a finance concept simply."
    ),
]

# Create a simple prompt template
prompt = PromptTemplate.from_template("""You are a helpful assistant that can use tools to answer questions.

Question: {input}

Available tools:
{tools}

Available tool names: [{tool_names}]

You must follow this exact sequence:
1. Use the appropriate tool to get the information
2. The tool's response will be your final answer

Example for concept explanation:
Question: What is compound interest?
Thought: I need to explain compound interest
Action: Concept Explainer
Action Input: compound interest
Observation: Compound interest is interest on both principal and accumulated interest.

{agent_scratchpad}

Begin!

Thought:""")

# Initialize LlamaCpp model
llm = LlamaCpp(
    model_path="C:\\Users\\karth\\models\\mistral-7b-instruct-v0.1.Q4_0.gguf",
    n_ctx=1024,
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
    max_iterations=2,
    return_intermediate_steps=True
)
