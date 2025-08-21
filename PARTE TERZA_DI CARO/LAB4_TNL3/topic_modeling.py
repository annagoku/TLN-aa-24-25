from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import utility as u
from umap import UMAP
from hdbscan import HDBSCAN
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.io as pio

pio.renderers.default = "browser"   # apre il grafico nel browser


def BERTTopic_modeling (model, umap_model, hdbscan_model, abstracts, embeddings):
    topic_model = BERTopic(
    embedding_model = model,
    umap_model = umap_model,
    hdbscan_model = hdbscan_model,
    verbose=True).fit(abstracts, embeddings)
    # Conta il numero di topic
    topic_info=topic_model.get_topic_info()
    print(topic_info)
    num_topics = len(topic_info)
    print(f"Numero di topic estratti: {num_topics}")
   
    return topic_model

    
def topic_visualization(topic_model):
    
    fig_barchart = topic_model.visualize_barchart(top_n_topics=10)
    fig_barchart.show()
   
    