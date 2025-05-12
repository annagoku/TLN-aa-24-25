import rich as r

import pandas as pd
from statistics import mean
import kagglehub
from kagglehub import load_dataset, KaggleDatasetAdapter
import kaggle
import nltk
import util as u
from nltk.tokenize import word_tokenize
nltk.download('punkt')  # scarica tokenizer
nltk.download('punkt_tab')


if __name__ == "__main__":

    # Nome del dataset da caricare
    dataset_name = 'rmisra/news-category-dataset'

    # Download del dataset direttamente in memoria (no disco)
    kaggle.api.dataset_download_files(dataset_name, path='.', unzip=True)

    # Load del dataset in pandas
  
    file_path = 'News_Category_Dataset_v3.json' 

    # Carica il dataset in pandas
    df_total = pd.read_json(file_path, encoding='utf-8', lines=True) #corregge la codifica e tratta ogni riga come un oggetto Json separato

    # Seleziona 10.000 righe casuali dal dataset
    df_sampled = df_total.sample(n=10000, random_state=42)

    # Imposta pandas per visualizzare tutte le colonne
    pd.set_option('display.max_columns', None)

    # Mostra le prime 5 righe del nuovo DataFrame
    print("Sampled 10,000 records:")
    print(df_sampled.head())

    # Mostra le prime 5 righe del dataset
    #print("First 5 records:")
    #print(df_total.head()) # funzione di Pandas che di default stampa le prime 5 righe

    sampled_sentece=df_sampled['headline'].tolist()

    pre_processed_sentence=[u.extraction_lemmi_from_sentence(word_tokenize(s)) for s in sampled_sentece ]

    for i in range(10):  # prime 10
      print(f"Frase: {sampled_sentece[i]}")
      print(f"Lemmi: {pre_processed_sentence[i]}\n")
