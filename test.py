# coding: utf-8
from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen3:4b-q4_K_M")
from langchain_core.messages import SystemMessage, HumanMessage
from synkenergytool import battery_state, grid_state, input_state
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model=llm, tools=[battery_state, grid_state, input_state])
system_message = (
    "You are an assistant that answers questions about a user's photovoltaic system "
    "including the inverter, batteries, input (e.g. solar panels), load and grid "
    "connection. NB: Positive power associated with the battery means that the battery "
    "is supplying power (the battery is discharging) while a negative power value "
    "means that the battery is charging."
)
sm = SystemMessage(system_message)
hm = HumanMessage("Is the battery charging? If so, is the battery being charged from the grid or the solar panels?")
#res = agent.invoke({"messages": [sm, hm]})
#print(res["messages"][-1].content)

for event in agent.stream({"messages": [sm, hm]}):
    update = event.get("agent", event.get("tools", {}))
    for message in update.get("messages", []):
        message.pretty_print()

