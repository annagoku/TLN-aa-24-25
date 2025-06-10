import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
from tkinter import scrolledtext
import ControllerGame as cg
import tkinter.messagebox
import numpy as ny
import simpleNLG as sp
import time
import spacy
from spacy import displacy
from pathlib import Path
import config as glvar
import Logic as l


nlp=spacy.load("en_core_web_sm")



def simulate_typing(widget, message, index=0, delay=50, submit_button=None, user_input=None, tag=None):
    """ Effetto di scrittura lettera per lettera su un widget di Tkinter. """
    if index == 0:
      glvar.is_typing= True
      if submit_button:
         submit_button.config(state='disabled')
      if user_input:
         user_input.delete(0, 'end')
         user_input.config(state='disabled')

    if index < len(message):
        widget.insert(tk.END, message[index], tag)
        widget.yview(tk.END)  # Scorri fino in fondo
        widget.after(delay, simulate_typing, widget, message, index + 1, delay, submit_button, user_input, tag)
    else:
        glvar.is_typing=False
        if submit_button:
           submit_button.config(state='normal')
        if user_input:
           user_input.config(state='normal')
        if glvar.end_game:
           glvar.gui.show_end_buttons()
           glvar.end_game=False

        if glvar.pending_message is not None:
            l.mng_dialog(glvar.pending_message, glvar.pending_chat_history, submit_button=submit_button, user_input=user_input)
            glvar.pending_message = None
            glvar.pending_chat_history = None


def parser_nen(frase):
    frase_parsata = nlp(frase)
    dict = {}
    for token in frase_parsata.ents:
        dict[token.text] = [token.text, token.start_char, token.end_char, token.label_]
    for key, value in dict.items():
        if "PERSON" in value:
            return key
    return None

def parser_proper_name(user_message):
    doc = nlp(user_message)  # Analizza la frase
    name = []
    # Estrarre tutte le entità riconosciute da spaCy
    for ent in doc.ents:
        name.append(ent.text)  # Aggiungi il testo dell'entità
    # Se NER non ha trovato nulla, cerca sostantivi propri (PROPN)
    if not name:
        for token in doc:
            if token.pos_ == "PROPN":  
                name.append(token.text)
   # Rimuove eventuali duplicati e verifica se la risposta corretta è tra i nomi estratti
    return name  # Restituisce True se `correct_answer` è tra i nomi estratti, altrimenti False


# Metodo per creare l'immagine del parsing
def displayParser(frase):
    svg = displacy.render(frase, style="dep")
    output_path = Path("result_spacy.svg")
    output_path.open("w", encoding="utf-8").write(svg)



#Funzione di parser parametrica per gestire le risposte che contengono una lista di oggetti 
def exstract_listed_words(user_message, correct_answer, key_word):
    """
    Estrae parole chiave (nomi) da una frase usando spaCy,
    evitando termini generici definiti dall'utente e privilegiando i sostantivi specifici.
    :param testo: La frase da analizzare
    :param parole_generiche: Lista di parole da escludere
    :return: Lista di parole chiave estratte
    """
    user_message = " ".join(user_message.split())  # Rimuove spazi multipli
    doc = nlp(user_message)
    
    # Converti parole generiche in un set per efficienza
    key_word_set = set(key_word)
    correct_answer_set=set(correct_answer)
    
    # Estrai i nomi (sostantivi) specifici
    # Estrai sostantivi comuni (NOUN) e nomi propri (PROPN)
    word_listed = [token.text.strip() for token in doc if token.pos_ in {"NOUN", "PROPN"} and token.text.strip() not in correct_answer_set]
    print(word_listed)
    # Se la frase contiene "and" o ",", dare priorità alle parole attorno a queste congiunzioni
    word_filtered = []
    for i, token in enumerate(doc):
        if token.text in {"and", ","} and i > 0 and i < len(doc) - 1:
            if doc[i - 1].pos_ in {"NOUN", "PROPN"} and doc[i - 1].lemma_ not in key_word_set:
                word_filtered.append(doc[i - 1].text.strip())
            if doc[i + 1].pos_ in {"NOUN", "PROPN"} and doc[i + 1].lemma_ not in key_word_set:
                word_filtered.append(doc[i + 1].text.strip())

     # Se word_listed contiene parole NON presenti tra le keyword, restituisci []
    if any(w.lower() not in key_word_set for w in word_listed):
        return []

    # Altrimenti, restituisci i filtrati (o vuoto se non ce ne sono)
    return word_filtered  



def check_answer_no_list(user_message, correct_answer, key_word, type):
    ordinal_stopwords = {"first", "second", "third", "fourth", "fifth", "last", "next", "previous","course"}
    if type=="binary": 
      correct_answer=str(correct_answer)
    user_message = user_message.replace(correct_answer, "")    
    doc_user_message = nlp(user_message.lower())    
    word_user = set()
    for token in doc_user_message:
        print(f"TOKEN: {token.text}, POS: {token.pos_}, LEMMA: {token.lemma_}")
        if token.pos_ in {"NOUN"} and token.lemma_.lower() not in ordinal_stopwords and token.text not in ordinal_stopwords:
            word_user.add(token.lemma_.lower())
    if type!="proper name":
      proper_names = parser_proper_name(user_message)
      for name in proper_names:
          word_user.add(name)
    print("Parole utente:", word_user)
    print("Risposta corretta:", correct_answer)
    word_keyword = set(key_word)
    print("Parole key:", word_keyword)
    if not word_user or word_user.issubset(word_keyword): #se l'insieme dei nomi della risposta dell'utente è un sottoinsieme dell'insieme delle keyword allora la risposta non contiene errori semantici 
        print("subset trovato:", word_user.issubset(word_keyword))
        return True
    print("subset trovato:", word_user.issubset(word_keyword))
    # Altrimenti, è errata
    return False
