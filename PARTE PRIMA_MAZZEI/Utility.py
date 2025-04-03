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


nlp=spacy.load("en_core_web_sm")



def simulate_typing(widget, message, index=0, delay=50):
    """ Effetto di scrittura lettera per lettera su un widget di Tkinter. """
    if index < len(message):
        widget.insert(tk.END, message[index])
        widget.yview(tk.END)  # Scorri fino in fondo
        widget.after(delay, simulate_typing, widget, message, index + 1, delay)


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
def exstract_listed_words(user_message, key_word):
    """
    Estrae parole chiave (nomi) da una frase usando spaCy,
    evitando termini generici definiti dall'utente e privilegiando i sostantivi specifici.
    :param testo: La frase da analizzare
    :param parole_generiche: Lista di parole da escludere
    :return: Lista di parole chiave estratte
    """
   
    doc = nlp(user_message)
    
    # Converti parole generiche in un set per efficienza
    key_word_set = set(key_word)
    
    # Estrai i nomi (sostantivi) specifici
    # Estrai sostantivi comuni (NOUN) e nomi propri (PROPN)
    word_listed = [token.text.strip() for token in doc if token.pos_ in {"NOUN", "PROPN"} and token.lemma_ not in key_word_set]
    
    # Se la frase contiene "and" o ",", dare priorità alle parole attorno a queste congiunzioni
    word_filtered = []
    for i, token in enumerate(doc):
        if token.text in {"and", ","} and i > 0 and i < len(doc) - 1:
            if doc[i - 1].pos_ in {"NOUN", "PROPN"} and doc[i - 1].lemma_ not in key_word_set:
                word_filtered.append(doc[i - 1].text.strip())
            if doc[i + 1].pos_ in {"NOUN", "PROPN"} and doc[i + 1].lemma_ not in key_word_set:
                word_filtered.append(doc[i + 1].text.strip())
    
    return word_filtered if word_filtered else word_listed