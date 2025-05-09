import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
from tkinter import scrolledtext
import ControllerGame as cg
import tkinter.messagebox
import numpy as ny
import simpleNLG as sp
import time
import Utility as u
import config as glvar
import spacy
import random as r
import Dao as d
from num2words import num2words


#Memorizzare a DB la singola risposta utente e il relativo punteggio

result=""
type=""
correct_answer=""
key_word=""
text=""
param=""
num_question=0

nlp=spacy.load("en_core_web_sm")





def mng_dialog(user_message, chat_history, submit_button, user_input):
    global text, num_question
    if glvar.is_typing:
       glvar.pending_message = user_message
       glvar.pending_chat_history = chat_history
       return
    if  glvar.state_dialog==-1 and glvar.player_name=='':
        Lara_response=sp.ask_info("name")
        glvar.started=True
        glvar.state_dialog=0
        u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input)
    elif glvar.state_dialog==0:
         name=u.parser_nen(user_message) #attenzione alla maiusola
         print(name)
         if name is None or name=='':
           Lara_response=sp.no_answer("your", "name")
           u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input)
         else:
            glvar.player_name=name
            d.save_name(glvar.player_name)
            glvar.state_dialog=1
            temp=sp.verb_subj("study", "you")
            Lara_response=" Hi! "+ name + ". Let's start! " + temp
            u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input)
    elif glvar.state_dialog==1 and num_question==0:           
            if 'not' in user_message.lower() or '\'t' in user_message.lower() or 'no' in user_message.lower():
                Lara_response="You're not brave enough for this challenge. See you next time"
                u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input)

                glvar.gui.show_end_buttons()

                #to do come interrompere il gioco es. disabilitare chat e invio

                
            elif 'yes' in user_message.lower() or 'of course' in user_message.lower() or 'i have studied' in user_message.lower():
                extracted_number=extract_question()
                d.save_question_made_for_player(extracted_number)
                print("Lo stato del dialogo è "+str(glvar.state_dialog))
                num_question=num_question+1
                print("Domanda "+ str(num_question))
                Lara_response="Well, we'll start then! " + sp.start_exam() + " The "+ num2words(num_question, to='ordinal')+" question is: " + text
                u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input)                
            else: 
               Lara_response="Please, let me know if you have studied. Don't make me waste time!"
               u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input) 

    elif (glvar.state_dialog==1 and num_question==1) or glvar.state_dialog==2  or glvar.state_dialog==3:
        if user_message is None or user_message=='':
            Lara_response="Please give me an answer right or wrong.Try!"
            u.simulate_typing(chat_history, "Lara: "+ Lara_response + "\n", submit_button=submit_button, user_input=user_input)
        else:
            
          d.save_answer_player(user_message, num_question)
          answer=mng_question(user_message, type, correct_answer, key_word)
          if answer:
            glvar.punteggio=glvar.punteggio+10
            print(glvar.punteggio)
            Lara_response="Good! Correct answer! You gain 10 points." 
            d.update_point_for_player(glvar.punteggio)
          else:
            Lara_response="Bad response! Sorry, no points gained."
        
          if glvar.state_dialog<3:
            glvar.state_dialog=glvar.state_dialog+1
            print("Lo stato del dialogo è "+ str(glvar.state_dialog))
            num_question=num_question+1
            print("Domanda"+ str(num_question))
            extracted_number=extract_question()       
            d.save_question_made_for_player(extracted_number)
            u.simulate_typing(chat_history, "Lara: "+ Lara_response + " "+ "Go on with the "+ num2words(num_question, to='ordinal')+" question. " + text +"\n", submit_button=submit_button, user_input=user_input)
      
          elif glvar.state_dialog==3:
              if glvar.punteggio<=10:
                  End_game="Only "+str(glvar.punteggio) +" points. "+"You lied when you said you had studied. Please, be honest next time. "            
              elif glvar.punteggio==20:
                  End_game=str(glvar.punteggio) +" points. "+"Good but not the best! My adventures are still too dangerous for you. "
              elif glvar.punteggio==30:
                  End_game=str(glvar.punteggio)+" points. "+"Well done! You are ready to take part to my next mission. "
              u.simulate_typing(chat_history, "Lara: "+ Lara_response + " "+"\n" + "Lara: "+ End_game, submit_button=submit_button, user_input=user_input)



def mng_question(user_message,type, correct_answer, key_word):
    answer = False 
    if type=="binary":
       answer=mng_question_binary(user_message, correct_answer)  
    elif type=="year":
      answer=mng_question_year(user_message, correct_answer)
    elif type=="number":
      answer=mng_question_number(user_message,correct_answer)
    elif type=="proper name":
      answer=mng_question_properName(user_message,correct_answer)
    elif type=="list":
      answer=mng_question_list(user_message, correct_answer, key_word)
    return answer

#Integra il controllo di correttezza con funzione di parsing per evitare risposte sematicamente scorrette
def mng_question_binary(user_message, correct_answer):
    if 'yes' in user_message.lower() or 'of course' in user_message.lower() or 'true' in user_message.lower() and correct_answer:
        answer=u.check_answer_no_list(user_message, correct_answer, key_word)
    else:
        answer=False
    return answer

def mng_question_year(user_message, correct_answer):
    if(
      correct_answer in user_message.lower() or correct_answer[2:4] in user_message.lower() 
       or num2words(int(correct_answer), lang='en') in user_message.lower() 
       or num2words(int(correct_answer[2:4])) in user_message.lower()
      ):
        answer=u.check_answer_no_list(user_message, correct_answer, key_word)
    else:
        answer=False
    return answer

def mng_question_number(user_message, correct_answer):
    if (correct_answer in user_message.lower() or num2words(int(correct_answer), lang='en') in user_message.lower()):
        answer=u.check_answer_no_list(user_message, correct_answer, key_word)
    else:
        answer=False
    return answer
    
def mng_question_properName(user_message,correct_answer):
    name=u.parser_proper_name(user_message)
    print(name)
    if correct_answer in name:
        answer=u.check_answer_no_list(user_message, correct_answer, key_word)
    else:
        answer=False
    return answer
   
def mng_question_list(user_message,correct_answer, key_word):
    
    word_filtered=u.exstract_listed_words(user_message, correct_answer, key_word)
    # Trova le parole che coincidono con quelle della risposta corretta
    matching_words = [word for word in word_filtered if word in correct_answer]
    # Stampa Input/Output per debug
    print(f" Input utente: {user_message}")
    print(f" Parole filtrate: {word_filtered}")
    print(f" Parole corrette attese: {correct_answer}")
    print(f" Matching trovato: {matching_words}")
    if len(matching_words) >= 2:
        answer=True
    else:
        answer=False
    return answer
    
    #popola le variabili globali relative  alla domanda e  restituisce il code  della  domanda
def extract_question():
    global result, type, correct_answer, key_word,text, param
    extracted=0
    print("Domanda estratta "+ str(extracted))
    while extracted in glvar.questions_made or extracted==0:
          extracted=r.randint(1, 7)
    print ("Domanda estratta e corretta "+ str(extracted))
    glvar.questions_made.append(extracted)
    result=d.retrieve_question_by_code(extracted)
    #text=result["question"]
    print(text)
    param=result["param"]
    type=result["type"]
    text=generate_question_text(type,param)
    print(type)
    correct_answer=result["answer"]
    #if type=="list":
    key_word=result["keyWord"]
    return extracted 

def generate_question_text(type, param):
    text=" "
    if type=="binary":
        if len(param) >= 3:  # Assicuriamoci che ci siano abbastanza elementi nel vettore
            subject, complement, action = param[0], param[1], param[2]
            text = sp.generate_true_false_question(subject, complement, action)
        else:
            print("Invalid parameters for binary question.")
    if type=="year":
         if len(param) >= 2:  # Assicuriamoci che ci siano abbastanza elementi nel vettore
            subject, event = param[0], param[1]
            text = sp.generate_when_question(subject, event)
         else:
            print("Invalid parameters for year question.")
    if type=="number":
         if len(param) >= 2:  # Assicuriamoci che ci siano abbastanza elementi nel vettore
            entity, subject = param[0], param[1]
            text = sp.generate_how_many_question(entity, subject)
         else:
            print("Invalid parameters for number question.")
    if type=="list":
        if len(param) >= 3:  # Assicuriamoci che ci siano abbastanza elementi nel vettore
            quantity, items, context = param[0], param[1], param[2]
            text = sp.generate_list_question(quantity, items, context)
        else:
            print("Invalid parameters for list question.")
    if type=="proper name":
        if param:   # Assicuriamoci che ci siano abbastanza elementi nel vettore
            entity = param[0]
            text = sp.generate_name_question(entity)
        else:
            print("Invalid parameters for proper name question.")       
    return text
      
 