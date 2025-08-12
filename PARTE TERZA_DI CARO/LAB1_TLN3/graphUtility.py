import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def compare_similarity_matrices(words, matrix1, matrix2, label1="WordNet", label2="Word2Vec"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    sns.heatmap(matrix1, xticklabels=words, yticklabels=words, cmap="YlGnBu", annot=True, annot_kws={"size": 8}, fmt=".2f", ax=axes[0])
    axes[0].set_title(f"Similarità {label1}")

    sns.heatmap(matrix2, xticklabels=words, yticklabels=words, cmap="YlGnBu", annot=True, annot_kws={"size": 8}, fmt=".2f", ax=axes[1])
    axes[1].set_title(f"Similarità {label2}")

    plt.tight_layout()
    plt.show()

def compare_similarity_matrices_with_diff(words, matrix1, matrix2, label1="WordNet", label2="Word2Vec"):
    diff_matrix = matrix2 - matrix1  # Word2Vec - WordNet
    print("Matrice delle differenze Word2Vec-WordNet", np.round(diff_matrix, 2))

    fig, axes = plt.subplots(1, 1, figsize=(20, 6))

    # Heatmap 3: Differenza
    cmap_diff = sns.diverging_palette(240, 10, as_cmap=True)  # Blu → Bianco → Rosso
    sns.heatmap(diff_matrix, xticklabels=words, yticklabels=words, cmap=cmap_diff,
                center=0, annot=True, annot_kws={"size": 8}, fmt=".2f", ax=axes)
    axes.set_title(f"Differenza: {label2} − {label1}")

    plt.tight_layout()
    plt.show()
