import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter
from nltk.corpus import wordnet as wn
import utility as u
from gensim.models import KeyedVectors
import simsem as simsem
import simlex as simlex


if __name__ == "__main__":
    

#Analisi della similarità semantica tramite simlex
    print("Analisi di similarità lessicale")
    definizioni_dict=u.create_dictionary()
    risultati_simlex=simlex.compute_simlex_for_category(definizioni_dict)
    for categoria, dati in risultati_simlex.items():
        media = dati["media_similarità"]
        matrice = dati["matrice_similarità"]
        print(f"{categoria}: media = {media}")
        #u.plot_similarity_matrix(matrice, categoria, similarity_type="lexical")

#Analisi della similarità tramite simsem
    print("Analisi di similarità semantica")
    model=u.load_word2vec_model()
    risultati_simsem=simsem.compute_simsem_for_category(definizioni_dict,model)
    for categoria, dati in risultati_simlex.items():
        media = dati["media_similarità"]
        matrice = dati["matrice_similarità"]
        print(f"{categoria}: media = {media}")
        #u.plot_similarity_matrix(matrice, categoria, similarity_type="semantic")

#Stampa risultati complessivi 
    u.plot_similarity_summary(risultati_simlex,risultati_simsem, u.category_metadata)

#Medie aggregate per dimensione

aggregati_simlex=u.aggrega_per_dimensione(risultati_simlex)
aggregati_simsem=u.aggrega_per_dimensione(risultati_simsem)

u.plot_similarity_by_dimension(aggregati_simlex, tipo="lexical")
u.plot_similarity_by_dimension(aggregati_simsem, tipo="semantic")
    
    

