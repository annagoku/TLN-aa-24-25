from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def w2v_similarity(w1, w2, model):
    if w1 in model and w2 in model:
        vec1 = model[w1].reshape(1, -1)
        vec2 = model[w2].reshape(1, -1)
        return cosine_similarity(vec1, vec2)[0][0]
    return 0


def build_w2v_similarity_matrix(words, model):
    n = len(words)
    matrix = np.zeros((n, n))
    for i, w1 in enumerate(words):
        for j, w2 in enumerate(words):
            matrix[i, j] = w2v_similarity(w1, w2, model)
    return matrix
