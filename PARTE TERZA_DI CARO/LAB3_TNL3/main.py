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




nltk.download('wordnet')
nltk.download('omw-1.4')

if __name__ == "__main__":

#Creazione di un dizionario categoria - lista definizioni lemmatizzate
    definizioni_dict=u.create_dictionary()
    dict_disambiguato=u.process_definizioni(definizioni_dict)
    u.print_rich_table(dict_disambiguato)