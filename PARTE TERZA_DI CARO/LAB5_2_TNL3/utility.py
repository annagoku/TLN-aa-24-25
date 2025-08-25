import csv
from nltk.corpus import stopwords
import re
from nltk.corpus import wordnet as wn
import pandas as pd
import numpy as np
import gensim.downloader as api
from deep_translator import GoogleTranslator



sigla_map = {
    "CS": {"concretezza": "concreto", "specificità": "specifico"},
    "CG": {"concretezza": "concreto", "specificità": "generico"},
    "AS": {"concretezza": "astratto", "specificità": "specifico"},
    "AG": {"concretezza": "astratto", "specificità": "generico"}
}

category_metadata={}
FILE='dataset_definizioni_TLN_25_en.csv'
N_TERMS=4


#Si parte dal file csv di definizioni già tradotto in inglese per motivi computazionali
def load_data_dict():
    global category_metadata
    definizioni_dict = {}
    count = 0

    with open(FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # salta intestazione

        for row in reader:
            if count >= N_TERMS:
                break
            if len(row) < 2:
                continue

            sigla = row[0].strip()
            concetto_en = row[1].strip()

            # Popola category_metadata
            if sigla in sigla_map:
                category_metadata[concetto_en] = sigla_map[sigla]
            else:
                category_metadata[concetto_en] = {"concretezza": "N/A", "specificità": "N/A"}

            # Definizioni in inglese
            definizioni_inglese = row[2:]

            if concetto_en not in definizioni_dict:
                definizioni_dict[concetto_en] = []
            definizioni_dict[concetto_en].extend(definizioni_inglese)

            count += 1

    return definizioni_dict




#Unifica i dati di due dizionari in modo da poter stampare la storia dell'intera interazione 
def unify_results_and_log(results, interaction_log):
    unified = []

    for result in results:
        concept = result["true_label"]
        entry = {
            "concept": concept,
            "interactions": interaction_log.get(concept, [])     
        }
        unified.append(entry)

    return unified

