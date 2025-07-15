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





'''''
category_metadata = {
    "Trousers": {
        "concretezza": "concreto",
        "specificità": "generico"
    },
    "Microscope": {
        "concretezza": "concreto",
        "specificità": "specifico"
    },
    "Heuristic": {
        "concretezza": "astratto",
        "specificità": "specifico"
    },
    "Danger": {
        "concretezza": "astratto",
        "specificità": "generico"
    }
}
'''



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
#N_DEFINITIONS = 32

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


###########Funzioni di pre-processsing#########################################

# Carica il modello pre-addestrato (es: Google News)
def load_word2vec_model(path='GoogleNews-vectors-negative300.bin'):
    model=api.load("glove-wiki-gigaword-100")
    return model

def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])

    
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
    # Lemmatizzazione
    lemmatized = [wn.morphy(t) if wn.morphy(t) else t for t in tokens_only_letters]
    # Restituisci una stringa (lemmi separati da spazi)
    return " ".join(lemmatized)


def create_dictionary():
    global N_TERMS, category_metadata
    definizioni_dict = {}

    category_metadata=load_category_metadata_from_csv(FILE)
    with open(FILE, "r", encoding='utf-8') as file:
        csv_reader=csv.reader(file,delimiter=";")
        next(csv_reader) #per skippare la prima riga dell'header   
        for row in csv_reader:
            if N_TERMS > 0:
                concetto=translate_it_to_en(row[1])
                definizioni=row[2:]
                if concetto not in definizioni_dict:
                    definizioni_dict[concetto] = []
                for definizione in definizioni:
                    lemmi= extraction_lemmi_from_sentence(definizione)
                    definizioni_dict[concetto].append(lemmi)
                N_TERMS-=1
    return definizioni_dict

def plot_similarity_matrix(matrix, category_name, similarity_type="semantic"):
    """
    Visualizza la matrice di similarità tra definizioni per una categoria.

    Parametri:
        matrix (np.array): matrice n x n di similarità
        category_name (str): nome della categoria/concept
        similarity_type (str): 'semantic' o 'lexical' (default: 'semantic')
    """
    assert similarity_type in {"semantic", "lexical"}, "similarity_type deve essere 'semantic' o 'lexical'"

    labels = [f"Def{i+1}" for i in range(len(matrix))]
    df = pd.DataFrame(matrix, index=labels, columns=labels)

    print(f"\n{similarity_type.capitalize()} Similarity Matrix for category: {category_name}")
    print(df.round(2))

    plt.figure(figsize=(10, 8))
    cmap = 'Blues' if similarity_type == "semantic" else 'Oranges'

    plt.imshow(matrix, cmap=cmap, interpolation='nearest')
    plt.colorbar(label=f'{similarity_type.capitalize()} Similarity')

    plt.xticks(ticks=np.arange(len(labels)), labels=labels, rotation=90)
    plt.yticks(ticks=np.arange(len(labels)), labels=labels)

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            val = matrix[i, j]
            plt.text(j, i, f"{val:.2f}", ha='center', va='center', color='black', fontsize=8)

    plt.title(f"{similarity_type.capitalize()} Similarity Matrix - {category_name}")
    plt.tight_layout()
    plt.show()



def plot_similarity_summary(simlex_dict, simsem_dict, category_metadata):
    """
    Crea una tabella grafica con matplotlib che mostra le medie SimLex e SimSem
    per ogni combinazione di specificità e concretezza.

    Parametri:
        simlex_dict (dict): {categoria: {"media_similarità": float, ...}}
        simsem_dict (dict): {categoria: {"media_similarità": float, ...}}
        category_metadata (dict): metadati per ogni categoria (concretezza, specificità)
    """
    

    # Etichette per righe e colonne
    rows = ["Generico", "Specifico"]
    cols = ["Astratto", "Concreto"]

    # Inizializza struttura matrice con testo per le celle
    cell_text = [["" for _ in cols] for _ in rows]

    # Riempimento delle celle con i valori medi
    for categoria in simlex_dict:
        concretezza = category_metadata[categoria]["concretezza"]
        specificità = category_metadata[categoria]["specificità"]

        simlex_val = simlex_dict[categoria]["media_similarità"]
        simsem_val = simsem_dict[categoria]["media_similarità"]

        r = 0 if specificità == "generico" else 1
        c = 0 if concretezza == "astratto" else 1

        entry = cell_text[r][c]
        if entry:
            entry += "\n"
        entry += f"SimLex: {simlex_val:.2f}\nSimSem: {simsem_val:.2f}"
        cell_text[r][c] = entry

    # Plot con matplotlib
    fig, ax = plt.subplots(figsize=(8, 5))
    table = plt.table(
        cellText=cell_text,
        rowLabels=rows,
        colLabels=cols,
        cellLoc='center',
        loc='center',
        colLoc='center',
        rowLoc='center'
    )

    table.scale(1, 2)
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    ax.axis('off')
    plt.title("Media Similarità Lessicale (SimLex) e Semantica (SimSem)", fontsize=14, weight='bold')
    plt.tight_layout()
    plt.show()

def aggrega_per_dimensione(sim_dict):
    """
    Aggrega le similarità per concretezza e specificità.

    Parametri:
        sim_dict (dict): dizionario con struttura:
            {
                categoria: {
                    "media_similarità": float,
                    "concretezza": "concreto"/"astratto",
                    "specificità": "generico"/"specifico"
                }
            }

    Ritorna:
        dict: {
            "concretezza": {"concreto": float, "astratto": float},
            "specificità": {"generico": float, "specifico": float}
        }
    """
    aggregati = {
        "concretezza": {"concreto": [], "astratto": []},
        "specificità": {"generico": [], "specifico": []}
    }

    for cat, valori in sim_dict.items():
        sim = valori["media_similarità"]
        conc = valori.get("concretezza")
        spec = valori.get("specificità")

        if conc in aggregati["concretezza"]:
            aggregati["concretezza"][conc].append(sim)
        if spec in aggregati["specificità"]:
            aggregati["specificità"][spec].append(sim)

    # Calcolo delle medie
    media_aggregata = {
        "concretezza": {
            k: round(np.mean(v), 4) if v else None
            for k, v in aggregati["concretezza"].items()
        },
        "specificità": {
            k: round(np.mean(v), 4) if v else None
            for k, v in aggregati["specificità"].items()
        }
    }

    return media_aggregata



def plot_similarity_by_dimension(aggregati, tipo="semantic"):
    """
    Visualizza due tabelle separate con le similarità medie per:
    - Concretezza (colonne: concreto vs astratto)
    - Specificità (colonne: generico vs specifico)
    
    Parametri:
        aggregati (dict): prodotto da `aggrega_per_dimensione()`
        tipo (str): "semantic" o "lexical" (usato nel titolo)
    """
    tipo = tipo.lower()
    titolo_base = "Similitudine Semantica" if tipo == "semantic" else "Similitudine Lessicale"

    # Dati per concretezza
    concretezza_labels = ["concreto", "astratto"]
    concretezza_data = [[aggregati["concretezza"].get("concreto", "")],
                        [aggregati["concretezza"].get("astratto", "")]]

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.axis('tight')
    ax1.axis('off')
    table1 = ax1.table(cellText=[list(map(str, [aggregati["concretezza"].get(lbl, "") for lbl in concretezza_labels]))],
                       colLabels=concretezza_labels,
                       rowLabels=[titolo_base],
                       cellLoc='center',
                       loc='center')
    table1.auto_set_font_size(False)
    table1.set_fontsize(12)
    table1.scale(1.2, 1.2)
    plt.title(f"{titolo_base} Concreto Vs Astratto", fontsize=13)
    plt.tight_layout()
    plt.show()

    # Dati per specificità
    specificita_labels = ["generico", "specifico"]
    specificita_data = [[aggregati["specificità"].get("generico", "")],
                        [aggregati["specificità"].get("specifico", "")]]

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.axis('tight')
    ax2.axis('off')
    table2 = ax2.table(cellText=[list(map(str, [aggregati["specificità"].get(lbl, "") for lbl in specificita_labels]))],
                       colLabels=specificita_labels,
                       rowLabels=[titolo_base],
                       cellLoc='center',
                       loc='center')
    table2.auto_set_font_size(False)
    table2.set_fontsize(12)
    table2.scale(1.2, 1.2)
    plt.title(f"{titolo_base} Specifico vs Generico", fontsize=13)
    plt.tight_layout()
    plt.show()






