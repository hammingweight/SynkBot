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

agent = create_react_agent(
    model=llm,
    tools=[
        battery_state,
        grid_state,
        input_state,
        inverter_settings,
        inverter_update,
        load_state,
    ],
)

class State(TypedDict):
    question: str
    messages: Annotated[list, add_messages]


def react(state: State):
    system_prompt = (
        "You are an assistant that answers questions about a user's photovoltaic system "
        "including the inverter, batteries, input (e.g. solar panels), load and grid "
        "connection. You do not have access to historic data. You can only access current "
        "data about the inverter, battery, grid and panels."
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{history}"),
            ("human", "{question}"),
        ]
    )
    messages = prompt.invoke(
        {"history": state["messages"], "question": state["question"]}
    )
    #print(dir(messages))
    print(len(messages.to_messages()))
    print(messages.to_messages())
    print("====================================")
    response = agent.invoke({"messages": messages.to_messages()})
    return {"messages": [HumanMessage(state["question"]), response["messages"][-1]]}


graph_builder = StateGraph(State)
graph_builder.add_node("react", react)

graph_builder.add_edge(START, "react")
graph_builder.add_edge("react", END)

memory = MemorySaver()
chatbot = graph_builder.compile(checkpointer=memory)