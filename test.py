# coding: utf-8
from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen3:4b-q4_K_M")
from langchain_core.messages import SystemMessage, HumanMessage
from synkenergytool.battery import battery_state
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model=llm, tools=[battery_state])
system_message = "You are an assistant that answers questions about a user's battery"
sm = SystemMessage(system_message)
hm = HumanMessage("Is the battery dangeroulsy hot?")
#res = agent.invoke({"messages": [sm, hm]})
#print(res["messages"][-1].content)

for event in agent.stream({"messages": [sm, hm]}):
    update = event.get("agent", event.get("tools", {}))
    for message in update.get("messages", []):
        message.pretty_print()

