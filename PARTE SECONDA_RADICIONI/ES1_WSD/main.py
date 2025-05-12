import rich as r
import util as u
import LeskAlgorithm as la
from nltk.wsd import lesk
from statistics import mean
import Table_fill as tf
import nltk

# Verifica e scarica le risorse NLTK se mancanti
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4')

nltk.download('semcor')


N_WORDS = 5
N_ATTEMPTS = 10

mean_accuracy_LESK_CODED = []
mean_accuracy_nltk_LESK = []

if __name__ == "__main__":
  for attempt in range(N_ATTEMPTS):
        print(f"\nIterazione #{attempt+1}")
        
        # Ottieni i termini dal corpus
        terms = u.extraction_terms_from_corpus(N_WORDS)

        # Popola la tabella e calcola le correttezze
        coded_correct_wsd, ntlk_correct_wds = tf.populate_results_table(terms, N_WORDS)       

        # Aggiungi le accuratezze medie
        mean_accuracy_LESK_CODED.append(coded_correct_wsd / N_WORDS)
        mean_accuracy_nltk_LESK.append(ntlk_correct_wds / N_WORDS)

  # Stampa le statistiche di accuratezza media
  print(f"\n\nAccuratezza media 'coded_LESK': {str(round((mean(mean_accuracy_LESK_CODED) * 100), 2))}%")
  print(f"\nAccuratezza media 'nltk_LESK': {str(round((mean(mean_accuracy_nltk_LESK) * 100), 2))}%")