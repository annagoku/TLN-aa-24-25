import nltk
from nltk.corpus import wordnet as wn
from gensim.models import KeyedVectors
import gensim.downloader as api
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import wordnetSimilarity as ws
import wordTwoVecSimilarity as wts
import graphUtility as gu

#Caricamento WordNet
nltk.download('wordnet')
nltk.download('omw-1.4')
#Modello di embeddings
model = api.load("glove-wiki-gigaword-100")

words = [
    # 1. Sinonimi/quasi sinonimi
    'giant', 'mountain', 'skyscraper',

    # 2. Concetti ambigui/polisemici
    'bank', 'money', 'river',

    # 3. Relazioni gerarchiche (iponimo–iperonimo)
    'dog', 'animal', 'cat',

    # 4. Associazioni funzionali (contesto d’uso)
    'car', 'road', 'driver',

    # 5. Concetti astratti vs concreti
    'freedom', 'justice', 'table',

    # 6. Categorie semantiche (gruppo coeso)
    'apple', 'banana', 'grape'
]


if __name__ == "__main__":
   
    matrixWordNet = ws.build_wn_similarity_matrix(words)
    print("Matrice di similarità WordNet", np.round(matrixWordNet, 2))

    matrixWord2Vec=wts.build_w2v_similarity_matrix(words, model)
    print("Matrice di similarità Word2Vec", np.round(matrixWord2Vec, 2))

    gu.compare_similarity_matrices(words, matrixWordNet, matrixWord2Vec)
    gu.compare_similarity_matrices_with_diff (words, matrixWordNet, matrixWord2Vec)
  