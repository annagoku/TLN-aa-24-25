import utility as u
import text_clustering as tc
import topic_modeling as tm


if __name__ == "__main__":

    #Caricamento dataset
    print("\033[32mData dictionary creation\033[0m")
    u.data_dict_creation()

    #Pipeline Text Clustering
    print("\033[32mEmbedding creation\033[0m")
    embeddings, model=tc.embeddings_creation(u.data_dict)
    print(embeddings.shape)
    print("\033[32mEmbedding reduced creation\033[0m")
    reduced_embeddings, umap_model=tc.dim_reduce(embeddings)
    print(reduced_embeddings.shape)
    print("\033[32mCluster creation\033[0m")
    clusters, hdbscan_model=tc.group_embeddings(reduced_embeddings)
    print("\033[32mPrint results and graph\033[0m")
    tc.print_abstracts_from_all_clusters(clusters, u.data_dict)
    tc.plot_umap_clusters(clusters, embeddings)

    #Pipeline Topic Modeling

    # Estrae gli abstract lemmatizzati
    abstracts = [item["abstract_lemmatized"] for item in u.data_dict.values()]
    print("\033[32mTopic model creation\033[0m")
    topic_model=tm.BERTTopic_modeling(model, umap_model, hdbscan_model, abstracts, embeddings)
    #titles = [item["title"] for item in u.data_dict.values()]
    print("\033[32mPrint topics\033[0m")
    tm.topic_visualization(topic_model, abstracts, tc.reduced_embeddings_2D)



