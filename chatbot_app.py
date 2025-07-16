import os
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import re

embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

st.title("SJSU Library Chatbot 🤖 (Free Local Mode)")
with st.spinner("Loading knowledge base..."):
    documents = SimpleDirectoryReader("knowledge_base").load_data()

index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# Avoid OpenAI completely by using "no_text" mode
query_engine = index.as_query_engine(response_mode="no_text")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("Ask me about SJSU Library services, staff, or forms")
user_input = st.text_input("You:")

if user_input:
    response = query_engine.query(user_input)
    response_text = ""

    user_words = set(user_input.lower().split())

    # Normalize and scan each line of text
    for node in response.source_nodes:
        lines = node.get_text().splitlines()
        for line in lines:
            plain_line = re.sub(r'\*\*|__|[#\-]', '', line).strip().lower()
            if any(word in plain_line for word in user_words):
                response_text = line.strip()
                break
        if response_text:
            break

    if not response_text:
        response_text = "No relevant information found."

    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", response_text))

for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")
