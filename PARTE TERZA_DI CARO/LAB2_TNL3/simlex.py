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
import numpy as np
import matplotlib.pyplot as plt
import gensim.downloader as api
import utility as u




def compute_simlex_for_category(definizioni_dict):
    """
    Calcola la similarità lessicale per ogni concetto usando l'overlap tra i lemmi delle definizioni.

    Parametri:
        definizioni_dict (dict): {concetto: [definizione1, definizione2, ...]} (lemmatizzate)
        category_metadata (dict): {concetto: {"concretezza": str, "specificità": str}}

    Ritorna:
        dict: {
            concetto: {
                "media_similarità": float,
                "matrice_similarità": np.array,
                "concretezza": str,
                "specificità": str
            }
        }
    """
    risultati = {}

    for concetto, definizioni in definizioni_dict.items():
        n = len(definizioni)
        matrix = np.zeros((n, n))

        # Preprocess: converti ogni definizione in un set di lemmi
        sets = [set(defn.split()) for defn in definizioni]

        # Calcola la similarità per ogni coppia
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0  # autosimilarità massima
                else:
                    intersection = sets[i] & sets[j]
                    union = sets[i] | sets[j]
                    sim = len(intersection) / len(union) if union else 0.0
                    matrix[i][j] = sim

        # Media solo sopra la diagonale
        mean_sim = np.mean(matrix[np.triu_indices_from(matrix, k=1)])

        # Salva risultati
        risultati[concetto] = {
            "media_similarità": round(mean_sim, 4),
            "matrice_similarità": matrix,
            "concretezza": u.category_metadata.get(concetto, {}).get("concretezza", "N/A"),
            "specificità": u.category_metadata.get(concetto, {}).get("specificità", "N/A")
        }

    return risultati




