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
import Logic as l
import config as glvar


class ChatBotGui: 
  def __init__(self):

  
    self.user_message=''

    self.window_game=tk.Tk()
    self.window_game.lift()
    self.window_game.grab_set()

    window_height = 750
    window_width = 1200
    self.window_game.title("Tomb Raider Challenge")
    self.window_game.configure(bg='black')
    self.window_game.resizable(False,False)
    screen_width = self.window_game.winfo_screenwidth()
    screen_height = self.window_game.winfo_screenheight()

    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))

    self.window_game.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

    # Carica l'immagine
    self.image = Image.open('LaraCroft.png')
    self.image = self.image.resize((314, 538))  # Ridimensiona l'immagine se necessario
    self.image = ImageTk.PhotoImage(self.image)
    
    
    # Crea un frame per l'immagine
    image_frame = tk.Frame(self.window_game)
    image_frame.pack(side="left", padx=20)  # Posizioniamo il frame a sinistra

  # Label con immagine
    image_label = tk.Label(image_frame, image=self.image)
    image_label.pack()  # L'immagine viene inserita nel frame dell'immagine

  # Crea un frame per la label e il campo di testo
    input_frame = tk.Frame(self.window_game, width=500, height=538, bg='black')
    input_frame.pack(side="left", padx=0, pady=50)  # Posizioniamo il frame a destra
    input_frame.pack_propagate(False)  # Blocca il ridimensionamento automatico

  # Label per il nome (posizionata a sinistra)
    self.chat_history = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=60, height=20, state='normal')
    self.chat_history.grid(row=0, column=0, padx=10, pady=20, sticky="e")  # Allineata a destra

  # Campo di testo (posizionato a destra della label)
    self.user_input = tk.Entry(input_frame, width=60)
    self.user_input.grid(row=1, column=0,padx=10, pady=5)

  # Pulsante di invio (posizionato sotto)
    self.submit_button = tk.Button(input_frame, font="Helvetica 14 bold", bg="grey", fg="white", text=glvar.text_button, command=self.mng_user_input)
    self.submit_button.grid(row=2, column=1, padx=5, sticky="e")

    self.window_game.after(1000, self.displayFirst_message)


  def change_text(self):
      glvar.text_button="Enter"
      self.submit_button.config(text=glvar.text_button)  # Aggiorna il pulsante

  def run(self):
      self.window_game.mainloop()
  
  def displayFirst_message(self):
      self.phrase=sp.build_phrase_complete("I", "be", "Lara Croft")
      u.simulate_typing(self.chat_history, "Lara: "+ "Hi! " + self.phrase + "\n")

  def mng_user_input(self):
      user_message = self.user_input.get().strip()
      if user_message!='' and glvar.state_dialog>=0:
         u.simulate_typing(self.chat_history, "Player: "+ user_message + "\n")
         self.user_input.delete(0, 'end')
         print(user_message)
         self.chat_history.after(2000, lambda: self.process_bot_response(user_message))  
      else: 
         self.change_text()
         l.mng_dialog(user_message, self.chat_history)  # Ottieni la risposta
      
     
  def process_bot_response(self, user_message):
      l.mng_dialog(user_message, self.chat_history)  # Ottieni la risposta
    