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
    topic_model.get_topic_info()
    topic_model.get_topic(4)
    


def topic_visualization(topic_model, data_dict, reduced_embeddings):
    fig = topic_model.visualize_documents(data_dict.titles, reduced_embeddings = reduced_embeddings, width = 1200, hide_annotations = True)
    fig.update_layout(font = dict(size = 16))
    topic_model.visualize_barchart()
    topic_model.visualize_hierarchy()
    topic_model.visualize_heatmap(n_clusters = 30)