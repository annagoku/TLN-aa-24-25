import csv
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.corpus import wordnet as wn
import pandas as pd
import numpy as np
from rich.table import Table
from rich.console import Console
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import matplotlib.pyplot as plt
import gensim.downloader as api
from gensim.models import Word2Vec
import spacy
import os
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer, util
from gensim.models import KeyedVectors

# Carica il modello linguistico
nlp = spacy.load("en_core_web_sm")


# Carica il modello per W2v
w2v_model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)



sigla_map = {
    "CS": {"concretezza": "concreto", "specificità": "specifico"},
    "CG": {"concretezza": "concreto", "specificità": "generico"},
    "AS": {"concretezza": "astratto", "specificità": "specifico"},
    "AG": {"concretezza": "astratto", "specificità": "generico"}
}

category_metadata={}
concetto_synsets_ammissibili = {}



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


def create_dictionary():
    global N_TERMS, category_metadata, FILE
    definizioni_dict = {}

    print("FASE 1: Conversione file definizioni da xlsx a csv")
    FILE = convert_xlsx_to_csv_if_not_exists("dataset_definizioni_TLN_25.xlsx")
    category_metadata = load_category_metadata_from_csv(FILE)

    # Nome del file CSV tradotto in inglese
    FILE_EN = FILE.replace(".csv", "_en.csv")

    # Se il CSV tradotto esiste già viene usato direttamente
    if os.path.exists(FILE_EN):
        print("File tradotto già presente:", FILE_EN)
        file_da_usare = FILE_EN
    else:
        print("File tradotto non trovato, traduzione avviata")
        with open(FILE, "r", encoding="utf-8") as fin, open(FILE_EN, "w", encoding="utf-8", newline="") as fout:
            reader = csv.reader(fin, delimiter=";")
            writer = csv.writer(fout, delimiter=";")

            header = next(reader)
            writer.writerow(header)  # copia l’header

            for row in reader:
                concetto_it = row[1]
                definizioni_it = row[2:]

                concetto_en = translate_it_to_en(concetto_it)
                definizioni_en = [translate_it_to_en(d) for d in definizioni_it]

                writer.writerow([row[0], concetto_en] + definizioni_en)

        file_da_usare = FILE_EN
        print("File tradotto salvato come:", FILE_EN)

    # Ora leggi dal file (già in inglese)
    with open(file_da_usare, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file, delimiter=";")
        next(csv_reader)  # salta l'header

        print("FASE 2: Creazione del dizionario concetto-definizioni")
        for row in csv_reader:
            if N_TERMS > 0:
                concetto = row[1]
                definizioni = row[2:]

                if concetto not in definizioni_dict:
                    definizioni_dict[concetto] = []

                for definizione in definizioni:
                    definizioni_dict[concetto].append({
                        "definizione": definizione
                    })

                N_TERMS -= 1
    #print("Stampa dizionario:", definizioni_dict)
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

    differentia_tokens = [token.lemma_ for token in doc if token.is_alpha and token.lemma_ != genus]
    differentia = " ".join(differentia_tokens)

    return genus, differentia

def score_against_definition_word2vec(synset, definizione, w2v_model):
    """
    Calcola la cosine similarity tra una definizione e la glossa di un synset usando Word2Vec.
    """
    # Lemmatizza definizione e glossa
    definizione_lemma = extraction_lemmi_from_sentence(definizione)
    synset_text = synset.definition()
    if synset.examples():
        synset_text += " " + " ".join(synset.examples())
    synset_lemma = extraction_lemmi_from_sentence(synset_text)

    # Funzione per ottenere vettore medio delle parole presenti nel modello
    def average_vector(text, model):
        tokens = text.split()
        vecs = [model[word] for word in tokens if word in model]
        if len(vecs) == 0:
            return np.zeros(model.vector_size)
        return np.mean(vecs, axis=0) #media colonna per colonna

    definizione_vec = average_vector(definizione_lemma, w2v_model)
    synset_vec = average_vector(synset_lemma, w2v_model)

    # Cosine similarity
    cosine_score = cosine_similarity([definizione_vec], [synset_vec])[0][0]

    return cosine_score

def explore_synset_tree(synset, definizione, depth=0, max_depth=2, visited=None):
    if visited is None:
        visited = set()
    
    # Evita ricorsione infinita o synset già visitati
    if synset in visited or depth > max_depth:
        return None, 0.0
    
    visited.add(synset)
    
    # Calcola punteggio con definizione
    best_synset = synset
    best_score = score_against_definition_word2vec(synset, definizione,w2v_model)
    
    # Esplora iponimi
    for hypo in synset.hyponyms():
        candidate_synset, score = explore_synset_tree(hypo, definizione, depth+1, max_depth, visited)
        if score > best_score:
            best_synset, best_score = candidate_synset, score
    
    return best_synset, best_score


def find_best_synset_by_genus_and_differentia(genus, definizione):
    synsets = wn.synsets(genus, pos=wn.NOUN)
    if not synsets:
        return None, -1

    best_synset = None
    best_score = -1

    for syn in synsets:
        candidate_synset, candidate_score = explore_synset_tree(syn, definizione)
        if candidate_score > best_score:
            best_score = candidate_score
            best_synset = candidate_synset

    return best_synset, best_score


def process_definizioni(definizioni_dict):
    global concetto_synsets_ammissibili
    print("FASE 3: Processamento definizioni")
    # Per ogni concetto, trova tutti i synset candidati (tutti i synset WordNet per quella parola)
    
    print("Lista synset ammissibili per concetto")
    for concetto in definizioni_dict.keys():
        # Cerca synset per lemma "concetto" e tutte le POS
        synsets = wn.synsets(concetto)  
        concetto_synsets_ammissibili[concetto] = [syn.name() for syn in synsets]

    for concetto, definizioni in definizioni_dict.items():
        print("Estrazione Genus e differentia per", concetto)
        for entry in definizioni:
            definizione = entry["definizione"]
            
            genus, differentia = extract_genus_and_differentia_dependency(definizione)
            entry["genus"] = genus
            entry["differentia"] = differentia

            #Disambiguazione solo se c'è genus
            if genus:
                #print("Navigazione ricorsiva iperonimi e iponimi per genus")
                synset, best_score = find_best_synset_by_genus_and_differentia(genus, definizione)
                entry["synset"] = synset.name() if synset else None
                entry["glossa"] = synset.definition() if synset else None
                entry["best_score"] = best_score
            else:
                entry["synset"] = None
                entry["glossa"] = None
                entry["best_score"] = "no_genus"

            #In ogni entry viene aggiunta la lista completa di synset candidati per il concetto
            entry["candidate_synsets_for_concept"] = concetto_synsets_ammissibili.get(concetto, [])

    return definizioni_dict


####################### Funzioni di stampa ########################################################

def get_score(entry):
    """
    Restituisce uno score numerico da usare per l'ordinamento.
    Se non disponibile o non numerico, ritorna -9999.
    """
    score = entry.get("best_score", None)
    try:
        return float(score)
    except (ValueError, TypeError):
        return -9999


def print_rich_table(definizioni_dict, top_n=5):
    """
    Stampa una tabella ordinata per punteggio discendente (best_score).
    Mostra solo i primi 'top_n' risultati per ogni concetto.
    """
    console = Console()
    table = Table(title=f"Risultati - Top {top_n} per concetto", show_lines=True)

    table.add_column("Categoria", style="cyan", no_wrap=True)
    table.add_column("Definizione_originale", style="white")
    table.add_column("Genus", style="yellow")
    table.add_column("Differentia", style="blue")
    table.add_column("Synset_best_score", style="magenta")
    table.add_column("Glossa_synset_best score", style="green")
    table.add_column("Best_score", style="green")
    table.add_column("Synset ammissibili per concetto", style="white")

    for concetto, entries in definizioni_dict.items():
        # Ordina con funzione helper
        sorted_entries = sorted(entries, key=get_score, reverse=True)

        # Prendi solo i primi top_n
        for entry in sorted_entries[:top_n]:
            table.add_row(
                str(concetto),
                str(entry.get("definizione", "—")),
                str(entry.get("genus", "—") or "—"),
                str(entry.get("differentia", [])) or "—",
                str(entry.get("synset", "—") or "—"),
                str(entry.get("glossa", "—") or "—"),
                str(entry.get("best_score", "—") or "—"),
                str(entry.get("candidate_synsets_for_concept", "—") or "—")
            )

    console.print(table)


