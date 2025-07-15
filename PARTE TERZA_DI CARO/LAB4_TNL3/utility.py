import csv
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.corpus import wordnet as wn
import pandas as pd
from rich.table import Table
from rich.console import Console
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
import gensim.downloader as api

import spacy
from datasets import load_dataset


# Carica il modello linguistico
nlp = spacy.load("en_core_web_sm")


# Carica il dataset (di default carica lo split "train")
dataset = load_dataset("librarian-bots/arxiv-metadata-snapshot", split="train", streaming=True)

def lemmatize_spacy(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.is_alpha]

def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])

# Controlla le colonne disponibili
print(dataset.column_names)

# Estrai titolo, abstract e categorie in un dizionario
# Usa 'id' o un contatore numerico come chiave
data_dict = {}

def data_dict_creation():
    global data_dict
    stop_words = set_stop_words()

    for i, item in enumerate(dataset):
        title = item.get("title", "").strip()
        abstract = item.get("abstract", "").strip()
        categories = item.get("categories", "").strip()

        # Lemmatizzazione dell'abstract
        cleaned_abstract = extraction_lemmi_from_sentence(abstract, stop_words)

        data_dict[i] = {
            "title": title,
            "abstract": abstract,
            "abstract_lemmatized": cleaned_abstract,
            "categories": categories
        }

        if i >= 10000:
            break

    print(f"Articoli estratti: {len(data_dict)}")
    print(data_dict[0])


def extraction_lemmi_from_sentence(sentence, stop_words):
    # Tokenizzazione
    tokens = word_tokenize(sentence)
    # Lowercase
    tokens_lower = [t.lower() for t in tokens]
    # Rimuovi stopword
    tokens_no_stop = [t for t in tokens_lower if t not in stop_words]
    # Rimuovi punteggiatura/numeri
    tokens_only_letters = [re.sub(r'[^a-z]', '', t) for t in tokens_no_stop if re.sub(r'[^a-z]', '', t)]
   # Ricostruisci frase pulita
    cleaned_text = " ".join(tokens_only_letters)
    # Lemmatizzazione con spaCy
    lemmatized = lemmatize_spacy(cleaned_text)
    return " ".join(lemmatized)