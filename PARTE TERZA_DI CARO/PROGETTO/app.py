import streamlit as st
import os
import signal
import time
from rag_utils import (
    get_prompt_template,
    load_documents,
    configure_models,
    parse_documents,
    setup_vector_store,
    build_index,
    build_query_engine
)

# -------------------------------
# Configurazione pagina Streamlit
# -------------------------------
st.set_page_config(page_title="RAG Horse Manual", layout="wide")

# Logo e copertina
st.image("logo_fise.jpg", width=200)
st.title("RAG Horse Manual")
st.image("copertina_manuale.jpg", width=400)
st.write("Enter your question and consult the FISE Horsemanship manual.")

# -------------------------------
# Setup iniziale (una tantum)
# -------------------------------
@st.cache_resource()
def initialize_system():
    prompt_template = get_prompt_template()
    documents = load_documents()
    configure_models()
    parsed_nodes = parse_documents(documents)
    vector_store = setup_vector_store()
    index = build_index(parsed_nodes, vector_store)
    return index, prompt_template

index, prompt_template = initialize_system()

# -------------------------------
# Campo query
# -------------------------------
user_input = st.text_input("Write your question here:")
TOP_K = 5  # numero massimo di chunk da recuperare

# Bottone invio query
if st.button("Submit"):
    if not user_input.strip():
        st.warning("Please enter a question before submitting.")
    else:
        try:
            with st.spinner("Processing your query... Retrieving chunks and generating answer..."):
                # Ricreazione retriever ad ogni query
                retriever = index.as_retriever(top_k=TOP_K)

                # Recupero chunk
                retrieved_nodes = retriever.retrieve(user_input)
                st.write(f"Number of chunks retrieved: {len(retrieved_nodes)}")

                # Creazione query engine
                query_engine, _ = build_query_engine(index, prompt_template, top_k=TOP_K)

                # Generazione risposta
                response = query_engine.query(user_input)

            # --- Risposta principale ---
            st.subheader("Generated Answer")
            st.markdown(f"**{response}**")

            # --- Chunks recuperati ---
            st.subheader("Retrieved Chunks")
            if retrieved_nodes:
                for i, node in enumerate(retrieved_nodes):
                    with st.expander(f"Chunk {i + 1} (Score: {node.score})"):
                        st.write(node.get_content())
            else:
                st.info("No relevant chunks found for this query.")

        except Exception as e:
            st.error(f"Error during answer generation: {e}")

# -------------------------------
# Pulsante Stop App
# -------------------------------
st.markdown("---")
if st.button("Stop App"):
    st.warning("The application has been stopped by the user. You can now close this tab.")
    time.sleep(5)  # lascia il tempo al frontend di aggiornarsi
    os.kill(os.getpid(), signal.SIGTERM)

