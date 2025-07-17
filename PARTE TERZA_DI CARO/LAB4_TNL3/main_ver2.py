import os
import numpy as np
import pickle
import json
from bertopic import BERTopic
import utility as u
import text_clustering as tc
import topic_modeling as tm

def save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":

    print("\033[32mData dictionary creation\033[0m")
    if not os.path.exists("data_dict.json"):
        u.data_dict_creation()
        with open("data_dict.json", "w", encoding="utf-8") as f:
            json.dump(u.data_dict, f, ensure_ascii=False, indent=2)
    else:
        print("Apro dict")
        with open("data_dict.json", "r", encoding="utf-8") as f:
            u.data_dict = json.load(f)

    print("\033[32mEmbedding creation\033[0m")
    if os.path.exists("embeddings.npy") and os.path.exists("embedding_model.pkl"):
        print("Carico embeddings and model")
        embeddings = np.load("embeddings.npy")
        model = load_pickle("embedding_model.pkl")
    else:
        embeddings, model = tc.embeddings_creation(u.data_dict)
        np.save("embeddings.npy", embeddings)
        save_pickle(model, "embedding_model.pkl")

    print("\033[32mEmbedding reduced creation\033[0m")
    if os.path.exists("reduced_embeddings.npy") and os.path.exists("umap_model.pkl"):
        print("Carico embeddingsreduced and UMAP model")
        reduced_embeddings = np.load("reduced_embeddings.npy")
        umap_model = load_pickle("umap_model.pkl")
    else:
        reduced_embeddings, umap_model = tc.dim_reduce(embeddings)
        np.save("reduced_embeddings.npy", reduced_embeddings)
        save_pickle(umap_model, "umap_model.pkl")

    print("\033[32mCluster creation\033[0m")
    if os.path.exists("clusters.pkl") and os.path.exists("hdbscan_model.pkl"):
        print("Carico cluster and hdbscan")
        clusters = load_pickle("clusters.pkl")
        hdbscan_model = load_pickle("hdbscan_model.pkl")
    else:
        clusters, hdbscan_model = tc.group_embeddings(reduced_embeddings)
        save_pickle(clusters, "clusters.pkl")
        save_pickle(hdbscan_model, "hdbscan_model.pkl")

    print("\033[32mPrint results and graph\033[0m")
    tc.print_abstracts_from_all_clusters(clusters, u.data_dict)
    tc.plot_umap_clusters(clusters, embeddings)

    print("\033[32mTopic model creation\033[0m")
    abstracts = [item["abstract_lemmatized"] for item in u.data_dict.values()]
    if os.path.exists("topic_model"):
        print("Carico topic model")
        topic_model = BERTopic.load("topic_model")
    else:
        topic_model = tm.BERTTopic_modeling(model, umap_model, hdbscan_model, abstracts, embeddings)
        topic_model.save("topic_model")

    print("\033[32mPrint topics\033[0m")
  
    tm.topic_visualization(topic_model, abstracts, tc.reduced_embeddings_2D)
