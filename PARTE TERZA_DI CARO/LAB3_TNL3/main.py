import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from collections import Counter
from nltk.corpus import wordnet as wn
import utility as u
from gensim.models import KeyedVectors
import os
import torch

if torch.cuda.is_available():
    print("GPU disponibile:", torch.cuda.get_device_name(0))
else:
    print("GPU non disponibile, si usa la CPU")


nltk.download('wordnet')
nltk.download('omw-1.4')

if __name__ == "__main__":

#Creazione di un dizionario categoria - definizioni
    definizioni_dict=u.create_dictionary()
    dict_disambiguato=u.process_definizioni(definizioni_dict)
    u.print_rich_table(dict_disambiguato)