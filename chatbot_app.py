import os
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

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
    response_text = "\n\n".join([node.get_text() for node in response.source_nodes])
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", response_text or "No relevant information found."))

for speaker, text in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {text}")
