import pickle
import numpy as np
import string
import re
from pyvi import ViTokenizer
import matplotlib.pyplot as plt
import nltk
import asyncio

from tkinter import *

pattern = r'[' + string.punctuation +']'
#from nltk.tokenize import word_tokenize

def summarize(sentences, scale_value):
    #Number of words in input text
    words_in = ViTokenizer.tokenize(sentences)
    words_in = re.sub(pattern, '', words_in)
    number_of_words_in = len(words_in.split())
    
    #split sentences - lowercase
    #sentences=sentences.lower().strip()
    sentences=sentences.strip()
#     print(sentences)
    
    sentences = nltk.sent_tokenize(sentences)
    
    number_of_sentences = len(sentences)
    
    
    import sklearn.model_selection
    from gensim.models import KeyedVectors 
    w2v = KeyedVectors.load_word2vec_format("./model/vi-300-5-30000-10-loss1.vec")
    
    vocab = w2v.key_to_index
    
    sentences_vec_array = []
    for sentence in sentences:
        sentence = re.sub(pattern, '', sentence)
        sentence = ViTokenizer.tokenize(sentence).strip()
        words = sentence.split()
        sentence_vec = np.zeros((300))
        for word in words:
            if word in vocab:
                sentence_vec+=w2v.key_to_index[word]
        sentences_vec_array.append(sentence_vec)
        
    #cluster
    from sklearn.cluster import KMeans

    #n_clusters = 5
    n_clusters = scale_value
#     n_clusters = round((number_of_sentences/8)*scale_value)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans = kmeans.fit(sentences_vec_array)
    
    #choose sentence for each cluster
    from sklearn.metrics import pairwise_distances_argmin_min

    avg = []
    for j in range(n_clusters):
        idx = np.where(kmeans.labels_ == j)[0]
        avg.append(np.mean(idx))

    closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, sentences_vec_array)
    ordering = sorted(range(n_clusters), key=lambda k: avg[k])
    summary = ''.join([sentences[closest[idx]] for idx in ordering])
    
    return summary
