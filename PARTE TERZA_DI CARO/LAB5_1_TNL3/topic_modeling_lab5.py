from sentence_transformers import SentenceTransformer
import utility as u
from umap import UMAP
from hdbscan import HDBSCAN
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import utility as u
from bertopic import BERTopic
import pickle

abstracts_lemmatized=[]
abstracts=[]
titles=[]


def embeddings_creation(data_dict):
    global abstracts_lemmatized, abstracts, titles
    # Estrai gli abstract lemmatizzati dal dizionario
    abstracts_lemmatized = [item["abstract_lemmatized"] for item in data_dict.values()]
    abstracts = [item["abstract"] for item in data_dict.values()]
    titles = [item["title"] for item in data_dict.values()]
    # Mapping a 3 vie: lemma -> (original, title)
    mapping = {lemma: (orig, title) for lemma, orig, title in zip(abstracts_lemmatized, abstracts, titles)}# pickle è nativo python
    with open("mapping.pkl", "wb") as f:
        pickle.dump(mapping, f)

    # Carica il modello
    model = SentenceTransformer("thenlper/gte-small")

    # Calcola gli embedding
    embeddings = model.encode(abstracts_lemmatized, show_progress_bar=True)
    return embeddings, model  # embeddings è un array numpy 

def dim_reduce(embeddings):
    umap_model = UMAP(n_components=5, min_dist=0.0, metric="cosine", random_state=42)
    reduced_embeddings = umap_model.fit_transform(embeddings)
    return reduced_embeddings, umap_model


def BERTTopic_modeling (model, umap_model, hdbscan_model, abstracts_lemmatized, embeddings):
    topic_model = BERTopic(
    embedding_model = model,
    umap_model = umap_model,
    hdbscan_model = hdbscan_model,
    verbose=True).fit(abstracts_lemmatized, embeddings)
    # Conta il numero di topic
    topic_info=topic_model.get_topic_info()
    #print(topic_info)
    num_topics = len(topic_info)
    print(f"Numero di topic estratti: {num_topics}")
   
    return topic_model

def topic_modeling_creation():
    print("Creazione del data dict")
    u.data_dict_creation()
    print("Creazione degli embeddings")
    embeddings, model=embeddings_creation(u.data_dict)
    print("Creazione degli embeddings ridotti")
    reduced_embeddings, umap_model=dim_reduce(embeddings)
    #clusters, hdbscan_model=group_embeddings(reduced_embeddings)
    hdbscan_model = HDBSCAN(min_cluster_size=50, metric="euclidean", cluster_selection_method="eom").fit(reduced_embeddings)
    print("Creazione del topic model")
    topic_model=BERTTopic_modeling(model, umap_model, hdbscan_model, abstracts_lemmatized, embeddings)
    return topic_model

