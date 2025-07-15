import utility as u
import text_clustering as tc


if __name__ == "__main__":
    print("Data dictionary creation")
    u.data_dict_creation()
    print("Embedding creation")
    embeddings=tc.embeddings_creation(u.data_dict)
    print(embeddings.shape)
    print("Embedding reduced creation")
    reduced_embeddings=tc.dim_reduce(embeddings)
    print("Cluster creation")
    clusters=tc.group_embeddings(reduced_embeddings)
    print("Print results and graph")
    tc.print_abstracts_from_all_clusters(clusters, u.data_dict)
    tc.plot_umap_clusters(clusters, embeddings)

