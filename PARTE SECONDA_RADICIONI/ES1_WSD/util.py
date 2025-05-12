import nltk
from nltk.corpus import semcor
from nltk.corpus.reader.wordnet import Lemma
import random as r
import re  #modulo regex
from nltk.corpus import wordnet as wn
from rich.console import Console
from rich.table import Table 

nltk.download('semcor')

#STOP_WORDS_FILE =  open(r"..../stop_words_FULL.txt", 'r')

LEN_SEMCOR = 37176 #len(semcor.sents())
print(len(semcor.sents()))
SEMCOR_TAGGED_SENTS = semcor.tagged_sents(tag='both') # salvataggio 37176 frasi annotate di semcor
SEMCOR_SENTS = semcor.sents() # salvataggio 37176 frasi di semcor


def extraction_lemmi_from_sentence(sentence):
    sentence_lower = [elem.lower() for elem in sentence] #parole in minuscolo
    sentence_without_stop_word = list(set(sentence_lower).difference(set_stop_words())) #rimuvo le stopwords
    sentence_only_letters = [re.sub(r'[^A-Za-z]+', '', x) for x in sentence_without_stop_word] # rimuovo la punteggiatura
    sentence_no_spaces = [ele for ele in sentence_only_letters if ele.strip()] # rimuovo gli spazi vuoti
    sentence_lemmatized = [wn.morphy(elem) for elem in sentence_no_spaces] # lista di lemmi
    return set(sentence_lemmatized)

def set_stop_words():
    with open("stop_words_FULL.txt", "r") as f:
        return set([row.strip() for row in f])

#funzione che restituisce una lista di cardinalità num_words termini ambigui rispetto a WordNet presi da semcor. Il numero di temini da cercare è dato come parametro
def extraction_terms_from_corpus(num_words):
    terms = []
    used_indices = []

    while len(terms) < num_words:
        # Estrai un indice finché non ne trovi uno non usato
        rand_index = r.randrange(0, LEN_SEMCOR - 1)
        while rand_index in used_indices:
            rand_index = r.randrange(0, LEN_SEMCOR - 1)

        used_indices.append(rand_index)
        sentence_tagged = SEMCOR_TAGGED_SENTS[rand_index]
        sentence_plain = SEMCOR_SENTS[rand_index]

        # Trova tutti i candidati validi nella frase
        candidate_nouns = []
        for chunk in sentence_tagged:
            if isinstance(chunk.label(), Lemma):
                if chunk[0].label() == 'NN':
                    word = chunk[0][0] #è una struttura ad albero 
                    if len(wn.synsets(word)) > 1:
                        candidate_nouns.append((word, chunk.label().synset()))

        # Se ci sono candidati validi, scegli uno a caso
        if candidate_nouns:
            word, synset = r.choice(candidate_nouns)
            terms.append([word, synset, sentence_plain])

    return terms

