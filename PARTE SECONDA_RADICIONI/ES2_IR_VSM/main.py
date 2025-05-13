from rich.table import Table
from rich.console import Console
import pandas as pd
import kagglehub
from kagglehub import load_dataset, KaggleDatasetAdapter
import kaggle
import nltk
import util as u
nltk.download('punkt')  # scarica tokenizer
nltk.download('punkt_tab')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NUM_QUERY=5
TOP_N=5

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

    #estrae dagli elementi campionati solo la headline e crea un lista
    sampled_sentece=df_sampled['headline'].tolist() 

    #pipeline
    vectorizer = TfidfVectorizer(lowercase=False, stop_words=None)
    pre_processed_sentence=[u.extraction_lemmi_from_sentence(s) for s in sampled_sentece ]
    '''
    for i in range(10):  # prime 10
      print(f"Frase: {sampled_sentece[i]}")
      print(f"Lemmi: {pre_processed_sentence[i]}\n")
    '''
    
    X_tfidf = u.pipeline_vectorize_training(pre_processed_sentence, vectorizer)

   #X_tfidf è una matrice sparsa (10.000 × max_features).Ogni riga è una frase. Ogni colonna è un termine del vocabolario. I valori sono i pesi TF-IDF.
    #E' una matrice sparsa

    # Stampa dimensioni e qualche esempio
    print("Shape della matrice TF-IDF:", X_tfidf.shape)
    #print("Parole usate nel vocabolario:", vectorizer.get_feature_names_out()[:10])  # prime 10
    #print("TF-IDF per il primo documento:\n", X_tfidf[0].toarray())

    queries=[]
    # Prompt per query multiple
    print(f"Inserisci {NUM_QUERY} query (una per volta):")
    for i in range(NUM_QUERY):
        q = input(f"Query {i+1}: ").strip()
        if q:
            queries.append(q)
    
    query_vector =u.pipeline_retrieval(queries, vectorizer)

    u.search_and_display_queries(query_vector, queries, X_tfidf, df_sampled, TOP_N)
        

    
