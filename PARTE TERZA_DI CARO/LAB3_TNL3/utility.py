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
import os
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer, util

# Carica il modello linguistico
nlp = spacy.load("en_core_web_sm")


# Carica il modello per embeddings (modello leggero e performante)
model = SentenceTransformer('all-MiniLM-L6-v2')


sigla_map = {
    "CS": {"concretezza": "concreto", "specificità": "specifico"},
    "CG": {"concretezza": "concreto", "specificità": "generico"},
    "AS": {"concretezza": "astratto", "specificità": "specifico"},
    "AG": {"concretezza": "astratto", "specificità": "generico"}
}

category_metadata={}


#FILE='definizioni.csv'
#FILE='definizioni_full.csv'
FILE=None
N_TERMS=4


########################## Funzioni di Pre-processing ##############################

def lemmatize_spacy(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.is_alpha]

def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])
    
def convert_xlsx_to_csv_if_not_exists(xlsx_path, sheet_name=0):
    # Costruisce il nome del file CSV a partire dal nome dell'XLSX
    csv_path = os.path.splitext(xlsx_path)[0] + ".csv"

    if os.path.exists(csv_path):
        print(f"Il file CSV esiste già: {csv_path}")
    else:
        # Legge il file Excel 
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        # Salva come CSV
        df.to_csv(csv_path, index=False, sep=";")
        print(f"File CSV creato: {csv_path}")
    return csv_path

def translate_it_to_en(text):
    try:
        #print(text)
        text_translated=GoogleTranslator(source='it', target='en').translate(text)
        #print(text_translated)
        return text_translated
    except Exception as e:
        print(f"Errore nella traduzione: {e}")
        return text
    
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
    print(category_metadata)
    return category_metadata

def extraction_lemmi_from_sentence(sentence):
    #Traduzione in inglese
    sentence_en=translate_it_to_en(sentence)
    # Tokenizzazione
    tokens = word_tokenize(sentence_en)
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


def create_dictionary():
    global N_TERMS, category_metadata, FILE
    definizioni_dict = {}
    
    FILE = convert_xlsx_to_csv_if_not_exists("dataset_definizioni_TLN_25.xlsx")
    category_metadata = load_category_metadata_from_csv(FILE)
    
    with open(FILE, "r", encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)  # salta l'header
        
        for row in csv_reader:
            if N_TERMS > 0:
                concetto = translate_it_to_en(row[1])
                definizioni = row[2:]
                
                if concetto not in definizioni_dict:
                    definizioni_dict[concetto] = []
                
                for definizione in definizioni:
                        definizione_en=translate_it_to_en(definizione)
                        #lemmi = extraction_lemmi_from_sentence(definizione)
                        definizioni_dict[concetto].append({
                            "definizione_lemmi": definizione_en
                        })
                
                N_TERMS -= 1
    
    #print("Dizionario in output:", definizioni_dict)
    return definizioni_dict



################### Funzioni di recupero Synset ###################

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

'''
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
    # cerca negli iponimi
    for hypo in syn.hyponyms():
        text = hypo.definition().lower() + " " + " ".join(hypo.examples()).lower()
        score = sum(1 for word in differentia if word.lower() in text)
        if score > best_score:
            best_score = score
            best_synset = hypo

    if best_synset is None:
        best_synset = synsets[0]
        strategy_used = "default_first_synset"

    return best_synset, strategy_used


def score_against_differentia(synset, differentia):
    text = synset.definition().lower() + " " + " ".join(synset.examples()).lower()
    score = sum(1 for word in differentia if word.lower() in text)
    return score
'''
def score_against_differentia(synset, differentia):
    # Prepara testo synset: definizione + esempi
    synset_text = synset.definition()
    if synset.examples():
        synset_text += " " + " ".join(synset.examples())

    # Prepara testo differentia: unisci lemmi in frase
    differentia_text = " ".join(differentia) if differentia else ""

    # Calcola embeddings
    embeddings = model.encode([synset_text, differentia_text])
    synset_emb, differentia_emb = embeddings[0], embeddings[1]

    # Calcola cosine similarity (range [-1,1], qui sempre >=0)
    cosine_score = util.cos_sim(synset_emb, differentia_emb).item()

    return cosine_score

def explore_synset_tree(synset, differentia, visited=None):
    if visited is None:
        visited = set()
    if synset in visited:
        return None, -1  # evita cicli
    visited.add(synset)

    best_synset = synset
    best_score = score_against_differentia(synset, differentia)

    # esplora ipernimi ricorsivamente
    for hyper in synset.hypernyms():
        candidate_synset, candidate_score = explore_synset_tree(hyper, differentia, visited)
        if candidate_score > best_score:
            best_score = candidate_score
            best_synset = candidate_synset

    # esplora iponimi ricorsivamente
    for hypo in synset.hyponyms():
        candidate_synset, candidate_score = explore_synset_tree(hypo, differentia, visited)
        if candidate_score > best_score:
            best_score = candidate_score
            best_synset = candidate_synset

    return best_synset, best_score

def find_best_synset_by_genus_and_differentia(genus, differentia):
    synsets = wn.synsets(genus, pos=wn.NOUN)
    if not synsets:
        return None, -1

    best_synset = None
    best_score = -1

    for syn in synsets:
        candidate_synset, candidate_score = explore_synset_tree(syn, differentia)
        if candidate_score > best_score:
            best_score = candidate_score
            best_synset = candidate_synset

    return best_synset, best_score


def process_definizioni(definizioni_dict):
    # Per ogni concetto, trova tutti i synset candidati (tutti i synset WordNet per quella parola)
    concetto_synsets_ammissibili = {}

    for concetto in definizioni_dict.keys():
        # Puoi cercare synset per lemma "concetto" e tutte le POS, oppure solo NOUN se preferisci
        synsets = wn.synsets(concetto)  
        concetto_synsets_ammissibili[concetto] = [syn.name() for syn in synsets]

    for concetto, definizioni in definizioni_dict.items():
        for entry in definizioni:
            definizione = entry["definizione_lemmi"]
            genus, differentia = extract_genus_and_differentia_dependency(definizione)
            entry["genus"] = genus
            entry["differentia"] = differentia

            # Qui fai la disambiguazione solo se c'è genus
            if genus:
                synset, best_score = find_best_synset_by_genus_and_differentia(genus, differentia)
                entry["synset"] = synset.name() if synset else None
                entry["glossa"] = synset.definition() if synset else None
                entry["best_score"] = best_score
            else:
                entry["synset"] = None
                entry["glossa"] = None
                entry["best_score"] = "no_genus"

            # Aggiungi in ogni entry la lista completa di synset candidati per il concetto
            entry["candidate_synsets_for_concept"] = concetto_synsets_ammissibili.get(concetto, [])

    return definizioni_dict


####################### Funzioni di stampa ########################################################

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
    table.add_column("Synset per concetto", style="white")

    for concetto, entries in definizioni_dict.items():
        for entry in entries:
            table.add_row(
                str(concetto),
                str(entry.get("definizione_originale", "—")),
                #str(entry.get("definizione_lemmi", "—")),
                str(entry.get("genus", "—") or "—"),
                " ".join(entry.get("differentia", [])) or "—",
                str(entry.get("synset", "—") or "—"),
                str(entry.get("glossa", "—") or "—"),
                str(entry.get("best_score", "—") or "—"),
                str(entry.get("candidate_synsets_for_concept", "—") or "—")
            )

    console.print(table)


