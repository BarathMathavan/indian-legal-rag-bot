import streamlit as st
from src.chain import rag_chain, retriever

st.set_page_config(page_title="NyayaAI - Indian Legal RAG Assistant", page_icon="⚖️", layout="wide")

st.title("⚖️ NyayaAI: Indian Legal Assistant (IPC/BNS)")
st.caption("Ask queries about Indian criminal law, penalties, and sections.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("E.g., What is the punishment for cheating under Section 420?")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Consulting Bare Acts and statutes..."):
            response = rag_chain.invoke(user_query)
            st.markdown(response)

            # Optional: Show retrieved references inside an expander
            with st.expander("🔎 View Retrieved Legal Sections"):
                retrieved_docs = retriever.invoke(user_query)
                for i, doc in enumerate(retrieved_docs):
                    st.markdown(f"**Document {i+1} (Section: {doc.metadata.get('section')}):**")
                    st.write(doc.page_content[:300] + "...")

    st.session_state.messages.append({"role": "assistant", "content": response})