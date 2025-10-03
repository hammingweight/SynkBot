from langchain_ollama import ChatOllama
from .battery import mocked_battery_state

llm = ChatOllama(model="qwen3:4b-q4_K_M")
result = llm.invoke("What is the battery temperature?", tools=[mocked_battery_state])
print(result)
