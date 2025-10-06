from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph import add_messages, StateGraph, START, END

from .battery import battery_state
from .grid import grid_state
from .input import input_state
from .inverter import inverter_settings, inverter_update
from .load import load_state

llm = ChatOllama(model="qwen3:4b-q4_K_M")
tools = [
    battery_state,
    grid_state,
    input_state,
    inverter_settings,
    inverter_update,
    load_state,
]
system_prompt = (
    "You are an assistant that answers questions about a user's photovoltaic system "
    "including the inverter, battery, input (e.g. solar panels), grid connection and the load."
    "The inverter is manufactured by SunSynk. You do not have access to historic data, "
    "aggregate data or trends. You can only access current, instantaneous data about the inverter, "
    "battery, solar panels, grid and load. Answer questions or instructions concisely."
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{history}"),
        ("human", "{question}\nRemember: Answer concisely."),
    ]
)
agent = prompt | create_react_agent(model=llm, tools=tools)


class State(TypedDict):
    question: str
    messages: Annotated[list, add_messages]


def react(state: State):
    index = len(state["messages"]) + 1
    # Write the messages to the console so the user can see the reasoning
    # and acting.
    for event in agent.stream(
        {"question": state["question"], "history": state["messages"]}
    ):
        while index < len(event["messages"]):
            message = event["messages"][index]
            message.pretty_print()
            index += 1

    # Add the user's question and the AI's message to the history.
    return {"messages": [HumanMessage(state["question"]), message]}


# Construct a chatbot
graph_builder = StateGraph(State)
graph_builder.add_node("react", react)
graph_builder.add_edge(START, "react")
graph_builder.add_edge("react", END)

memory = MemorySaver()
chatbot = graph_builder.compile(checkpointer=memory)
