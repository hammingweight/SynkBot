import uuid
import streamlit as st

from synkbot import chatbot


# Qwen3 prefixes its answer with thinking. We don't want to pollute
# the output with that detail.
def remove_thinking_tags(message):
    message = message.strip()
    if message.startswith("<think>"):
        index = message.index("</think>") + len("</think>")
        message = message[index:].strip()
    return message


st.set_page_config(page_title="SynkBot", page_icon="🇮🌞")
st.markdown(
    "<h2 style='text-align: center;'>Welcome to SynkBot!</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<center><h4>An AI Chatbot for talking to your SunSynk® Inverter 🌞</h4></center>",
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(remove_thinking_tags(message["content"]))

if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())


def process_message(message, user_id):
    config = {"configurable": {"thread_id": user_id}}
    response = chatbot.invoke({"question": message}, config=config)
    return remove_thinking_tags(response["messages"][-1].content)


if user_message := st.chat_input("How can I help you with your solar installation?"):
    with st.chat_message("user"):
        st.markdown(user_message)
    st.session_state.chat_history.append({"role": "User", "content": user_message})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = process_message(user_message, st.session_state["user_id"])
        st.markdown(response)
    st.session_state.chat_history.append({"role": "Assistant", "content": response})
