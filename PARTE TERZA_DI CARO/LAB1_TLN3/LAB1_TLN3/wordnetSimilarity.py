import nltk
from nltk.corpus import wordnet as wn
import numpy as np

#Calcolo della similarità in Wordnet come distanza tra i synset
def wn_similarity(w1, w2):
    syns1 = wn.synsets(w1, pos=wn.NOUN)  # Limita ai nomi per compatibilità path_similarity
    syns2 = wn.synsets(w2, pos=wn.NOUN)
    if syns1 and syns2:
        sims = [s1.path_similarity(s2) for s1 in syns1 for s2 in syns2 if s1.path_similarity(s2)]
        return max(sims) if sims else 0
    return 0

#Costruzione della matrice di similarità
def build_wn_similarity_matrix(words):
    n = len(words)
    matrix = np.zeros((n, n))
    for i, w1 in enumerate(words):
        for j, w2 in enumerate(words):
            matrix[i, j] = wn_similarity(w1, w2)
    return matrix