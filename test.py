# coding: utf-8
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from synkenergytool import battery_state, grid_state, input_state, load_state

llm = ChatOllama(model="qwen3:4b-q4_K_M")

agent = create_react_agent(
    model=llm, tools=[battery_state, grid_state, input_state, load_state]
)
system_message = (
    "You are an assistant that answers questions about a user's photovoltaic system "
    "including the inverter, batteries, input (e.g. solar panels), load and grid "
    "connection. NB: Positive power associated with the battery means that the battery "
    "is supplying power (the battery is discharging) while a negative power value "
    "means that the battery is charging."
)
sm = SystemMessage(system_message)
hm = HumanMessage(
    "How much power is my home using?"
)
# res = agent.invoke({"messages": [sm, hm]})
# print(res["messages"][-1].content)

for event in agent.stream({"messages": [sm, hm]}):
    update = event.get("agent", event.get("tools", {}))
    for message in update.get("messages", []):
        message.pretty_print()
