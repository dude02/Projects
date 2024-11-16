import os
import tempfile
import streamlit as st
from streamlit_chat import message
from webquery import WebQuery
import trafilatura

st.set_page_config(page_title="Website to Chatbot")

# Function to display the messages in the chat
def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

# Function to process the user input
def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking..."):
            try:
                query_text = st.session_state["webquery"].ask(user_text)
            except Exception as e:
                query_text = f"Error processing your request: {str(e)}"

        st.session_state["messages"].append((user_text, True))  # Add user message
        st.session_state["messages"].append((query_text, False))  # Add bot's response

# Function to ingest content from a URL
def ingest_input():
    if st.session_state["input_url"] and len(st.session_state["input_url"].strip()) > 0:
        url = st.session_state["input_url"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Ingesting content..."):
            try:
                ingest_text = st.session_state["webquery"].ingest(url)
            except Exception as e:
                ingest_text = f"Error ingesting the URL: {str(e)}"
        st.session_state["messages"].append((ingest_text, False))  # Show feedback from ingestion

# Check if the OpenAI API key is set
def is_openai_api_key_set() -> bool:
    return len(st.session_state["OPENAI_API_KEY"]) > 0

# Main function to run the Streamlit app
def main():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["url"] = ""
        st.session_state["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
        if is_openai_api_key_set():
            st.session_state["webquery"] = WebQuery(st.session_state["OPENAI_API_KEY"])
        else:
            st.session_state["webquery"] = None

    # App header
    st.header("Website to Chatbot")

    # Input for the OpenAI API Key
    if st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password"):
        if (
            len(st.session_state["input_OPENAI_API_KEY"]) > 0
            and st.session_state["input_OPENAI_API_KEY"] != st.session_state["OPENAI_API_KEY"]
        ):
            st.session_state["OPENAI_API_KEY"] = st.session_state["input_OPENAI_API_KEY"]
            st.session_state["messages"] = []
            st.session_state["user_input"] = ""
            st.session_state["input_url"] = ""
            st.session_state["webquery"] = WebQuery(st.session_state["OPENAI_API_KEY"])

    # Input for the URL to ingest
    st.subheader("Add a URL")
    st.text_input("Input URL", value=st.session_state["url"], key="input_url", disabled=not is_openai_api_key_set(), on_change=ingest_input)

    st.session_state["ingestion_spinner"] = st.empty()

    # Display the chat messages
    display_messages()

    # Input for user message
    st.text_input("Message", key="user_input", disabled=not is_openai_api_key_set(), on_change=process_input)

    # Divider and source code link
    st.divider()
    st.markdown("Source code: [Github](https://github.com/Anil-matcha/Website-to-Chatbot)")

# Run the Streamlit app
if __name__ == "__main__":
    main()

