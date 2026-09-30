__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from src.chain import rag_chain, retriever

st.set_page_config(
    page_title="NyayaAI - Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Header
st.title("⚖️ NyayaAI: Indian Legal & Procedural Assistant")
st.markdown(
    "Query Indian statutory laws, police investigation procedures, bail guidelines, and criminal statutes."
)
st.divider()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI Legal Assistant powered by Indian Bare Acts and Procedural Manuals. How can I assist your legal research today?"
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
user_query = st.chat_input("Ask a question (e.g., 'What is the procedure for anticipatory bail under CrPC?')")

if user_query:
    # Append & display user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing Bare Acts and relevant legal provisions..."):
            try:
                # 1. Fetch LLM answer
                response = rag_chain.invoke(user_query)
                st.markdown(response)

                # 2. Show citations/references in an expandable box
                with st.expander("🔎 View Retrieved Legal References"):
                    docs = retriever.invoke(user_query)
                    for i, doc in enumerate(docs, 1):
                        source = doc.metadata.get("source_document", "Unknown Act")
                        st.markdown(f"**Reference {i}: {source}**")
                        st.caption(doc.page_content[:400] + "...")
                        st.divider()

                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)