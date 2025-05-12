import random as r
from nltk.corpus import wordnet as wn
import re


def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])
    

def extraction_lemmi_from_sentence(sentence):
    sentence_lower = [elem.lower() for elem in sentence] #parole in minuscolo
    sentence_without_stop_word = list(set(sentence_lower).difference(set_stop_words())) #rimuvo le stopwords
    sentence_only_letters = [re.sub(r'[^A-Za-z]+', '', x) for x in sentence_without_stop_word] # rimuovo la punteggiatura
    sentence_no_spaces = [ele for ele in sentence_only_letters if ele.strip()] # rimuovo gli spazi vuoti
    sentence_lemmatized = [wn.morphy(elem) for elem in sentence_no_spaces] # lista di lemmi
    return set(sentence_lemmatized)