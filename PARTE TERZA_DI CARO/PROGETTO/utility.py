# utility.py
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# Modello transformer per embedding
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L6-v2"

# Caricamento tokenizer e modello solo una volta
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def load_dataset(file_path, chunk_size=300):
    """
    Carica il file di testo e lo suddivide in blocchi.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Split basato su lunghezza
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def embed_chunk(chunk):
    """
    Calcola l'embedding del testo usando un modello transformer.
    """
    inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # Media dei token embeddings
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

def build_faiss_index(embeddings, vector_dim):
    """
    Costruisce un indice FAISS da una lista di vettori.
    """
    import faiss
    index = faiss.IndexFlatL2(vector_dim)
    index.add(np.array(embeddings).astype("float32"))
    return index

def embed_query(query):
    """
    Calcola embedding per una query di ricerca.
    """
    return embed_chunk(query)

