from sentence_transformers import SentenceTransformer
import utility as u
from umap import UMAP
from hdbscan import HDBSCAN
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import utility as u

reduced_embeddings_2D=[]

def embeddings_creation(data_dict):
    # Estrai gli abstract lemmatizzati dal dizionario
    abstracts = [item["abstract_lemmatized"] for item in data_dict.values()]

    # Carica il modello
    model = SentenceTransformer("thenlper/gte-small")

    # Calcola gli embedding
    embeddings = model.encode(abstracts, show_progress_bar=True)

    return embeddings, model  # embeddings è un array numpy 

def dim_reduce(embeddings):
    umap_model = UMAP(n_components=5, min_dist=0.0, metric="cosine", random_state=42)
    reduced_embeddings = umap_model.fit_transform(embeddings)
    return reduced_embeddings, umap_model

def group_embeddings(reduced_embeddings):
    hdbscan_model = HDBSCAN(min_cluster_size=50, metric="euclidean", cluster_selection_method="eom").fit(reduced_embeddings)
    clusters = hdbscan_model.labels_
    print(len(set(clusters)))
    return clusters, hdbscan_model

def print_abstracts_from_all_clusters(clusters, data_dict):
   

    unique_clusters = np.unique(clusters)

    for cluster_id in sorted(unique_clusters):
        indices = np.where(clusters == cluster_id)[0]

        print(f"\n=== 📊 Cluster {cluster_id} — {len(indices)} abstract trovati ===\n")

        for i in indices:
            title = data_dict[i].get("title", "No title")
            abstract = data_dict[i].get("abstract_lemmatized", "")[:300]  # primi 300 caratteri
            #print(f"📄 {title}\n📝 {abstract}...\n")


def plot_umap_clusters(clusters, embeddings, titles=None, sample_size=u.NUM_ARTICLE):
    """
    Visualizza i cluster in uno scatter plot UMAP.
    
    Parameters:
    - reduced_embeddings: ndarray, UMAP embeddings ridotti (es. shape [N, 2])
    - clusters: array/list con etichette di clustering (es. da HDBSCAN)
    - titles: lista opzionale con i titoli degli articoli
    - sample_size: quanti punti visualizzare (default 1000)
    """
    global reduced_embeddings_2D

    reduced_embeddings_2D = UMAP(n_components=2, min_dist=0, metric="cosine", random_state=42).fit_transform(embeddings)
    # Crea il DataFrame UMAP
    df = pd.DataFrame(reduced_embeddings_2D[:sample_size], columns=["x", "y"])
    
    if titles:
        df["title"] = titles[:sample_size]
    else:
        df["title"] = [f"Abstract {i}" for i in range(sample_size)]

    df["cluster"] = [str(c) for c in clusters[:sample_size]]

    # Separazione outlier / cluster validi
    to_plot_df = df[df["cluster"] != "-1"]
    outliers_df = df[df["cluster"] == "-1"]

    # Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(outliers_df.x, outliers_df.y, alpha=0.5, s=2, c="grey", label="Outliers")
    plt.scatter(
        to_plot_df.x, to_plot_df.y,
        c=to_plot_df.cluster.astype(int),
        alpha=0.6, s=3, cmap="tab20b", label="Clusters"
    )
    plt.axis("off")
    plt.title("Visualizzazione UMAP dei Cluster", fontsize=14)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()
