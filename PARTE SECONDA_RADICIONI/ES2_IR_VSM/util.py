import random as r
from rich.table import Table
from rich.console import Console
import pandas as pd
from nltk.corpus import wordnet as wn
import re
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

console = Console()

#Partendo dal file crea un set di stop words
def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])
    


def extraction_lemmi_from_sentence(sentence):
    # Tokenizzazione - suddivisione di una frase in token (parole, numeri, punteggiatura)
    tokens = word_tokenize(sentence)
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

#vectorizer.fit prende in ingresso una lista di stringhe
def pipeline_vectorize_training (sentences, vectorizer):
    pre_processed_sentence=[extraction_lemmi_from_sentence(s) for s in sentences ]
    X_tfidf = vectorizer.fit_transform(pre_processed_sentence) #fit_transform funzione da usare per i dati di partenza
    return X_tfidf


def pipeline_retrieval (queries, vectorizer):
    pre_processed_queries=[extraction_lemmi_from_sentence(q) for q in queries ]
    query_matrix = vectorizer.transform(pre_processed_queries)
    return query_matrix

def search_and_display_queries(query_matrix, queries, X_tfidf, df_sampled, TOP_N):
    for q_idx, query in enumerate(queries):
        print(f"\nTop {TOP_N} risultati per: '{query}'")

        # Calcola le similarità per la query corrente
        similarities = cosine_similarity(query_matrix[q_idx], X_tfidf).flatten()
        top_indices = np.argsort(similarities)[::-1][:TOP_N]

        # Crea la tabella
        table = Table(title=f"Top {TOP_N} risultati per: '{query}'")
        table.add_column("Score", justify="right", style="cyan")
        table.add_column("Headline", style="bold")
        table.add_column("Category", style="green")

        # Aggiungi i risultati nella tabella
        for idx in top_indices:
            # Nessun controllo sugli indici, assumendo che siano validi
            table.add_row(
                f"{similarities[idx]:.3f}",
                df_sampled.iloc[idx]['headline'],
                df_sampled.iloc[idx]['category']
            )

        # Stampa la tabella
        console.print(table)
