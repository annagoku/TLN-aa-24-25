import nltk
from nltk.corpus import semcor
from nltk.corpus.reader.wordnet import Lemma
import random
import re
from nltk.corpus import wordnet as wn
import util as u


def lesk_algorithm(term, sentence):
    
    set_sentence = u.extraction_lemmi_from_sentence(sentence) #pre-processa la frase in modo da aver un set di parole significative in forma di lemma
    best_sense = wn.synsets(term)[0] #inizializzare il best_sense con il primo synset del termine 
    max_overlap = 0  #inizializzazione del valore di overlap da massimizzare
   
    for sense in wn.synsets(term): #ciclo sui synset del termine considerato
        info_collected_fromWn = []
        for example in sense.examples():
            info_collected_fromWn = info_collected_fromWn + example.split() #colleziona in info_collected gli esempi del synset su cui il ciclo è posizionato
        for glos in sense.definition().split():
            info_collected_fromWn =  info_collected_fromWn + re.sub(r"[^a-zA-Z0-9]", "", glos).split() #colleziona in info_collected le glosse private della punteggiatura sulla definizione del synset trattato
            #dopo aver accumulato tutte le frasi relative ad un termine ed ad un suo senso in info_collected
        set_infoWn_filtered = u.extraction_lemmi_from_sentence(info_collected_fromWn) #set di lemmi dalle info collezionate da wordNet
        overlap = len(set_infoWn_filtered.intersection(set_sentence)) #guardo gli elementi in comune tra info_collected e la frase passata in input
        if overlap > max_overlap: #chi ha più termini in comune farà si che il synset trattato diventi il best_synset
            max_overlap = overlap
            best_sense = sense

    return best_sense