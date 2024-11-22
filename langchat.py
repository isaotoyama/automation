import json
import operator
from pprint import pprint
from typing import Annotated, Optional, Sequence, TypedDict, List

from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path = "/Users/nausicaa/Documents/GitHub/auto/.env"
load_dotenv(dotenv_path)

# Retrieve the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

print(f"Loaded OpenAI API Key: {openai_api_key[:5]}***")  # Debugging masked key output

# Import ChatOpenAI from langchain-openai
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.load import dumps, loads
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

# Custom imports
from functions.cache.cache_utils import get_llm_memory, store_llm_memory
from functions.lexbot import LexBot


# Type definitions
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# Constants
DECISION_AND_RESPONSE_PROMPT = """
You are a smart orchestrator facilitating communication between a user and a Lex bot. Do not make any reference of the bot to the user.
Follow these guidelines:
Clarifying Questions:
If the Lex bot asks the user a question, and the user responds with a clarifying question, address the user's query directly.
DO NOT RESPOND TO ANY QUESTIONS FROM THE USER THAT ARE NOT RELATED TO THE CONVERSATION. Politely tell them you have no idea.
"""

# Global variables
bot: Optional[LexBot] = None
model = ChatOpenAI(
    temperature=0,
    streaming=True,
    model_name="gpt-4o",
    openai_api_key=openai_api_key  # Use the key loaded from .env
)


def filter_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """Filter messages to keep the last 10 and the first message."""
    if len(messages) <= 10:
        return messages
    return messages[:1] + messages[-10:]


# Tool definitions
@tool("lex_bot", return_direct=True)
def lex_bot(text: str, session_id: Optional[str] = None) -> str:
    """Returns the bot prompt."""
    if not bot:
        raise ValueError("LexBot instance is not initialized.")
    return bot.get_bot_response(text, session_id)


# Setup tools
tools = [lex_bot]
functions = [convert_to_openai_function(t) for t in tools]


def should_continue(state: AgentState) -> str:
    """Determine whether to continue or end the workflow."""
    messages = state["messages"]
    last_message = messages[-1]
    return "continue" if "function_call" in last_message.additional_kwargs else "end"


def call_model(state: AgentState) -> AgentState:
    """Handle model invocation."""
    messages = state["messages"]
    filtered_messages = filter_messages(messages)
    human_input = filtered_messages[-1].content
    if "hello code" in human_input.lower():
        return {
            "messages": [
                AIMessage(
                    content="",
                    additional_kwargs={
                        "function_call": {
                            "arguments": f'{{"text":"{human_input}"}}',
                            "name": "lex_bot",
                        }
                    },
                )
            ]
        }
    response = model.invoke(filtered_messages)
    return {"messages": [response]}


def call_tool(state: AgentState, config: dict) -> AgentState:
    """Call tools based on the last message."""
    messages = state["messages"]
    last_message = messages[-1]
    session_id = config["configurable"].get("session_id")
    if not session_id:
        raise ValueError("Session ID is missing in the configuration.")

    arguments = json.loads(last_message.additional_kwargs["function_call"]["arguments"])
    arguments.update({"session_id": session_id})
    print(f"Calling Bot with {arguments}")
    action = ToolNode(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=arguments,
    )
    print(f"The agent action is {action}")
    response = action.invoke()
    print(f"The tool result is: {response}")
    function_message = FunctionMessage(content=json.dumps(response), name=action.tool)
    return {"messages": [function_message]}


def llm_bot(llm_bot_input: str, user_id: str, lex_bot_instance: LexBot) -> dict:
    """Main LLM Bot orchestrator."""
    global bot
    bot = lex_bot_instance

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tool)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent", should_continue, {"continue": "action", "end": END}
    )
    workflow.add_edge("action", END)
    app = workflow.compile()

    system_message = SystemMessage(content=DECISION_AND_RESPONSE_PROMPT)
    user_input = HumanMessage(content=llm_bot_input)

    messages = get_llm_memory(user_id)
    inputs = {
        "messages": loads(messages) + [user_input]
        if messages
        else [system_message, user_input]
    }
    output = app.invoke(inputs, {"configurable": {"session_id": user_id}})
    print("STATE:")
    pprint(output)
    print("END STATE")
    store_llm_memory(dumps(output.get("messages")), user_id)

    if output.get("messages")[-1].type == "function":
        return json.loads(output.get("messages")[-1].content)
    return {"messages": [{"content": output.get("messages")[-1].content}]}
