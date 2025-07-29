# retrieve.py
import os
import pickle
import faiss
from utility import load_dataset, embed_chunk, build_faiss_index, embed_query
import numpy as np
import ollama

# File persistenti
TEXT_DB_PATH = "text_db.pkl"
FAISS_INDEX_PATH = "faiss_index.idx"
EMBEDDING_DIM = 384  # per MiniLM

def load_or_create_index(file_path):
    """
    Carica indice FAISS e base di conoscenza, oppure li genera.
    """
    if os.path.exists(TEXT_DB_PATH) and os.path.exists(FAISS_INDEX_PATH):
        print("🔄 Caricamento indice e base di conoscenza esistenti...")
        with open(TEXT_DB_PATH, "rb") as f:
            text_db = pickle.load(f)
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        print("⚙️ Generazione nuova base di conoscenza...")
        text_db = load_dataset(file_path)
        embeddings = [embed_chunk(chunk) for chunk in text_db]
        faiss_index = build_faiss_index(embeddings, EMBEDDING_DIM)
        with open(TEXT_DB_PATH, "wb") as f:
            pickle.dump(text_db, f)
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        print("✅ Indice salvato.")
    return text_db, faiss_index

def retrieve(query, text_db, faiss_index, top_k=5):
    """
    Trova i chunk più simili alla query.
    """
    query_emb = embed_query(query).astype("float32").reshape(1, -1)

     # 🔍 DEBUG: Verifica dimensioni
    print(f"[DEBUG] Query embedding shape: {query_emb.shape}")
    print(f"[DEBUG] FAISS index dimension: {faiss_index.d}")

    distances, indices = faiss_index.search(query_emb, top_k)
    results = [(text_db[i], distances[0][j]) for j, i in enumerate(indices[0])]
    return results

def generate_answer(query, retrieved_knowledge):
    # Pulizia chunk e concatenazione
    context_text = "\n".join(chunk.strip() for chunk, _ in retrieved_knowledge if len(chunk.strip()) > 20)

    prompt = f"""
    You are an experienced riding instructor, skilled in training, equine ethology, and horse anatomy.
    The context provided will be about horse and it is taken from Horsemanship manual.
    Answer the question **strictly using the context below** and include any **relevant facts** you find only in the context. Be concise but informative.
    Don't add comments or information not included in the context.
    **IMPORTANT** if the context doesn't contain useful information for the answer, say that you are not able to answer.

    Contesto:
    {context_text}

    Domanda:
    {query}
    """
    stream = ollama.chat(
        model="mistral:7b-instruct-q4_0",
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': query},
        ],
        stream=True,
    )
    return stream


