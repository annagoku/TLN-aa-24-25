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
# Caricamento modello Word2Vec (esempio con GoogleNews)
#model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin.gz", binary=True)
#model = api.load("word2vec-google-news-300")
model = api.load("glove-wiki-gigaword-100")

words = ['dog', 'cat', 'car', 'vehicle', 'apple', 'fruit']


if __name__ == "__main__":
    matrixWordNet = ws.build_wn_similarity_matrix(words)
    print(np.round(matrixWordNet, 2))

    matrixWord2Vec=wts.build_w2v_similarity_matrix(words, model)
    print(np.round(matrixWordNet, 2))

    gu.compare_similarity_matrices(words, matrixWordNet, matrixWord2Vec)
    gu.compare_similarity_matrices_with_diff (words, matrixWordNet, matrixWord2Vec)