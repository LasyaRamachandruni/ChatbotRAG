
import os
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import OpenAI

openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

st.title("SJSU Library Chatbot 🤖")

with st.spinner("Loading knowledge base..."):
    documents = SimpleDirectoryReader("knowledge_base").load_data()

service_context = ServiceContext.from_defaults(llm=OpenAI(api_key=openai_api_key))
index = VectorStoreIndex.from_documents(documents, service_context=service_context)
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("Ask me about SJSU Library services, staff, or forms")
user_input = st.text_input("You:")

if user_input:
    response = chat_engine.chat(user_input)
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", response.response))

for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")
