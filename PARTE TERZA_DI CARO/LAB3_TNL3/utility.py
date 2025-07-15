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

# Carica il modello linguistico
nlp = spacy.load("en_core_web_sm")



category_metadata = {
    "Animal": {
        "concretezza": "concreto",
        "specificità": "generico"
    },
    "Bicycle": {
        "concretezza": "concreto",
        "specificità": "specifico"
    },
    "Justice": {
        "concretezza": "astratto",
        "specificità": "specifico"
    },
    "Emotion": {
        "concretezza": "astratto",
        "specificità": "generico"
    }
}


FILE='definizioni.csv'
#FILE='definizioni_full.csv'
N_TERMS=4


def lemmatize_spacy(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.is_alpha]

def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])

def create_dictionary():
    global N_TERMS
    definizioni_dict = {}
    with open(FILE, "r", encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)  # salta header
        for row in csv_reader:
            if N_TERMS > 0:
                concetto = row[0]
                definizioni = row[1:]
                if concetto not in definizioni_dict:
                    definizioni_dict[concetto] = []
                for definizione in definizioni:
                    lemmi = extraction_lemmi_from_sentence(definizione)
                    definizioni_dict[concetto].append({
                        "definizione_originale": definizione,
                        "definizione_lemmi": lemmi
                    })
                N_TERMS -= 1
    return definizioni_dict


def extraction_lemmi_from_sentence(sentence):
    # Tokenizzazione
    tokens = word_tokenize(sentence)
    # Lowercase
    tokens_lower = [t.lower() for t in tokens]
    # Rimuovi stopword
    tokens_no_stop = [t for t in tokens_lower if t not in set_stop_words()]
    # Rimuovi punteggiatura/numeri
    tokens_only_letters = [re.sub(r'[^a-z]', '', t) for t in tokens_no_stop if re.sub(r'[^a-z]', '', t)]
   # Ricostruisci frase pulita
    cleaned_text = " ".join(tokens_only_letters)
    # Lemmatizzazione con spaCy
    lemmatized = lemmatize_spacy(cleaned_text)
    return " ".join(lemmatized)

#Estrazione genus e differentia

def extract_genus_and_differentia_dependency(definizione):
    doc = nlp(definizione)

    genus = None
    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ == "NOUN":
            genus = token.lemma_
            break
    if genus is None:
        for token in doc:
            if token.dep_ in {"nsubj", "nsubjpass"} and token.pos_ == "NOUN":
                genus = token.lemma_
                break
    if genus is None:
        for token in doc:
            if token.pos_ == "NOUN":
                genus = token.lemma_
                break

    differentia = [token.lemma_ for token in doc if token.is_alpha and token.lemma_ != genus]

    return genus, differentia


def find_best_synset(genus, differentia):
    if not genus:
        return None, "no_genus"

    synsets = wn.synsets(genus, pos=wn.NOUN)
    if not synsets:
        return None, "no_synsets_for_genus"

    best_synset = None
    best_score = 0
    strategy_used = "direct_match"

    for syn in synsets:
        text = syn.definition().lower() + " " + " ".join(syn.examples()).lower()
        score = sum(1 for word in differentia if word.lower() in text)
        if score > best_score:
            best_score = score
            best_synset = syn

    if best_score == 0:
        strategy_used = "hypernym_fallback"
        for syn in synsets:
            for hyper in syn.hypernyms():
                text = hyper.definition().lower() + " " + " ".join(hyper.examples()).lower()
                score = sum(1 for word in differentia if word.lower() in text)
                if score > best_score:
                    best_score = score
                    best_synset = hyper

    if best_synset is None:
        best_synset = synsets[0]
        strategy_used = "default_first_synset"

    return best_synset, strategy_used


def process_definizioni(definizioni_dict):
    for concetto, definizioni in definizioni_dict.items():
        for entry in definizioni:
            definizione = entry["definizione_lemmi"]
            genus, differentia = extract_genus_and_differentia_dependency(definizione)
            synset, strategy = find_best_synset(genus, differentia) if genus else (None, "no_genus")
            entry["genus"] = genus
            entry["differentia"] = differentia
            entry["synset"] = synset.name() if synset else None
            entry["glossa"] = synset.definition() if synset else None
            entry["strategia_synset"] = strategy
    return definizioni_dict


def print_rich_table(definizioni_dict):
    console = Console()
    table = Table(title="Risultati - Definizioni & Synset", show_lines=True)

    table.add_column("Categoria", style="cyan", no_wrap=True)
    table.add_column("Definizione originale", style="white")
    table.add_column("Lemmi", style="dim")
    table.add_column("Genus", style="yellow")
    table.add_column("Differentia", style="blue")
    table.add_column("Synset", style="magenta")
    table.add_column("Glossa", style="green")
    table.add_column("Strategy for synset", style="white")

    for concetto, entries in definizioni_dict.items():
        for entry in entries:
            table.add_row(
                concetto,
                entry.get("definizione_originale", "—"),
                entry.get("definizione_lemmi", "—"),
                entry.get("genus", "—") or "—",
                " ".join(entry.get("differentia", [])) or "—",
                entry.get("synset", "—") or "—",
                entry.get("glossa", "—") or "—",
                entry.get("strategia_synset", "—") or "—"
            )

    console.print(table)


