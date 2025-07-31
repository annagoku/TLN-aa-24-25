import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
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
from deep_translator import GoogleTranslator




sigla_map = {
    "CS": {"concretezza": "concreto", "specificità": "specifico"},
    "CG": {"concretezza": "concreto", "specificità": "generico"},
    "AS": {"concretezza": "astratto", "specificità": "specifico"},
    "AG": {"concretezza": "astratto", "specificità": "generico"}
}

category_metadata={}

def translate_it_to_en(text):
    try:
        #print(text)
        text_translated=GoogleTranslator(source='it', target='en').translate(text)
        #print(text_translated)
        return text_translated
    except Exception as e:
        print(f"Errore nella traduzione: {e}")
        return text



FILE='dataset_definizioni_TLN_25.csv'
N_TERMS=4

def load_category_metadata_from_csv(FILE, max_rows=4):
    global category_metadata 

    with open(FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')  # o ',' a seconda del file
        next(reader)  # Salta intestazione
        count = 0
        for row in reader:
            if count >= max_rows:
                break
            if len(row) < 2:
                continue  # salta righe incomplete

            sigla =row[0].strip()
            categoria = translate_it_to_en(row[1].strip())

            if sigla in sigla_map:
                category_metadata[categoria] = sigla_map[sigla]
            else:
                # Default o gestione errori
                category_metadata[categoria] = {"concretezza": "N/A", "specificità": "N/A"}

            count += 1
    print("Passo 1: ", category_metadata)
    return category_metadata

def create_dictionary():
    global N_TERMS, category_metadata
    definizioni_dict = {}

    category_metadata = load_category_metadata_from_csv(FILE)
    with open(FILE, "r", encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)  # salta l'intestazione

        for row in csv_reader:
            if N_TERMS > 0:
                concetto = translate_it_to_en(row[1])
                definizioni_italiano = row[2:]

                # Traduci tutte le definizioni in inglese
                print("Traduzione delle definizioni in inglese del concetto: ", concetto)
                definizioni_inglese = [translate_it_to_en(definizione) for definizione in definizioni_italiano]

                # Aggiungi al dizionario
                if concetto not in definizioni_dict:
                    definizioni_dict[concetto] = []
                definizioni_dict[concetto].extend(definizioni_inglese)

                N_TERMS -= 1

    return definizioni_dict


def unify_results_and_log(results, interaction_log):
    unified = []

    for result in results:
        concept = result["true_label"]
        entry = {
            "concept": concept,
            "true_label": concept,
            "interactions": interaction_log.get(concept, []),
            "final_guess": result["final_label"],
            "final_prompt": result["user_prompt"],
            "final_definition": result["definition"]
        }
        unified.append(entry)

    return unified

