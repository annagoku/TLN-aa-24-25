import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter
from nltk.corpus import wordnet as wn
import pandas as pd
from rich.table import Table
from rich.console import Console
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import KeyedVectors
import numpy as np
import matplotlib.pyplot as plt
import gensim.downloader as api
import utility as u



def get_sentence_embedding(sentence, model):
    words = u.extraction_lemmi_from_sentence(sentence).split()
    vectors = [model[word] for word in words if word in model]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(model.vector_size)

def compute_simsem_for_category(definizioni_dict, model):
    """
    Calcola la similarità semantica media e la matrice di similarità per ogni categoria
    nel dizionario di definizioni.

    Parametri:
        definizioni_dict (dict): dizionario con chiave = categoria, valore = lista di definizioni (lemmatizzate)
        model: modello Word2Vec o GloVe

     Ritorna:
        dict: {categoria: {"media_similarità": float, "matrice_similarità": np.array,
                           "concretezza": str, "specificità": str}}
    """
    result_dict_simsem = {}

    for categoria, definizioni in definizioni_dict.items():
        embeddings = [get_sentence_embedding(defn, model) for defn in definizioni]
        matrix = cosine_similarity(np.vstack(embeddings))
        mean_sim = np.mean(matrix[np.triu_indices_from(matrix, k=1)])
        result_dict_simsem[categoria] = {
            "media_similarità": round(mean_sim, 4),
            "matrice_similarità": matrix,
            "concretezza": u.category_metadata.get(categoria, {}).get("concretezza", "N/A"),
            "specificità": u.category_metadata.get(categoria, {}).get("specificità", "N/A")
        }

    return result_dict_simsem



