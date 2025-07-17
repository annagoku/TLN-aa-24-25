from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import utility as u
from umap import UMAP
from hdbscan import HDBSCAN
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd





def BERTTopic_modeling (model, umap_model, hdbscan_model, abstracts, embeddings):
    topic_model = BERTopic(
    embedding_model = model,
    umap_model = umap_model,
    hdbscan_model = hdbscan_model,
    verbose=True).fit(abstracts, embeddings)
    info=topic_model.get_topic_info()
    print(info)
    #topic_model.get_topic(4)
    return topic_model

def diagnose_topics(topics):
    print(f"Tipo di topics_: {type(topics)}")
    print(f"Lunghezza topics_: {len(topics)}")
    print("Prime 20 voci con tipo e contenuto:")
    for i, t in enumerate(topics[:20]):
        print(f"Index {i}: Tipo={type(t)}, Valore={t}")
        if isinstance(t, np.ndarray):
            print(f"  -> shape: {t.shape}, dtype: {t.dtype}, contenuto (flat): {list(t.flat)}")

    
def clean_topics(topics):
    cleaned = []
    for t in topics:
        if isinstance(t, np.ndarray):
            if t.size == 1:
                cleaned.append(int(t.item()))
            else:
                cleaned.append(int(t.flat[0]))
        else:
            cleaned.append(int(t))
    return cleaned


    
def topic_visualization(topic_model, abstracts, reduced_embeddings_2D):
    print("✅ Tipo documenti:", type(abstracts[0]))
    print("✅ Tipo embedding:", type(reduced_embeddings_2D))
    print("✅ Embedding shape:", reduced_embeddings_2D.shape)

    fig = topic_model.visualize_documents(
        abstracts,
        reduced_embeddings=reduced_embeddings_2D,
        width=1200,
        hide_annotations=True
    )
    fig.update_layout(font=dict(size=16))
    fig_barchart = topic_model.visualize_barchart()
    fig_barchart.show()
    #topic_model.visualize_hierarchy()
    #topic_model.visualize_heatmap(n_clusters = 30)
    #fig.show()