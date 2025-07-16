import os
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Use sentence-transformers for local embedding
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

# Load documents
st.title("SJSU Library Chatbot 🤖 (Free Local Mode)")
with st.spinner("Loading knowledge base..."):
    documents = SimpleDirectoryReader("knowledge_base").load_data()

# Build index
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=False)

# Streamlit chat UI
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

