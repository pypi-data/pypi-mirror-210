from sklearn.metrics.pairwise import cosine_similarity
from pprint import pprint


def similarity(sentences, model, time_start, threshold):
    sentence_embeddings = model.encode(sentences)
    similarities = []
    for i in range(1, len(sentence_embeddings)):
        score = cosine_similarity(sentence_embeddings[i-1].reshape(1, -1), sentence_embeddings[i].reshape(1, -1))[0][0]
        similarities.append(score)

    timecodes = []  # момент времени когда происходит деление на блоки
    for i in range(len(similarities)):
        if similarities[i] < threshold:
            timecodes.append(time_start[i+1])
    return similarities, timecodes
