import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
from tkinter import scrolledtext
import ControllerGame as cg
import tkinter.messagebox
import numpy as ny
import simpleNLG as sp
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
    ''''
    self.image = Image.open('LaraCroft_Black.png')
    self.image = self.image.resize((314, 600))  # Ridimensiona l'immagine se necessario
    self.image = ImageTk.PhotoImage(self.image)
    '''
    self.load_image_with_black_background('LaraCroft_Black.png', (314, 700))
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

    #Campo di chat
    self.chat_history = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=60, height=20, state='normal')
    self.chat_history.grid(row=0, column=0, padx=10, pady=20, sticky="e")  # Allineata a destra
    self.chat_history.tag_configure("player", foreground="blue")
    self.chat_history.tag_configure("lara", foreground="darkred")

  # Campo per inserimento di testo 
    self.user_input = tk.Entry(input_frame, width=60)
    self.user_input.grid(row=1, column=0,padx=10, pady=5)

  # Pulsante di invio (posizionato sotto)
    self.submit_button = tk.Button(input_frame, font="Helvetica 14 bold", bg="grey", fg="white", width=10, text=glvar.text_button, command=self.mng_user_input)
    self.submit_button.grid(row=3, column=1, padx=(0, 5), sticky="e")

    self.window_game.after(1000, self.displayFirst_message)
  
  # Pulsante di uscita (inizialmente nascosto)
    self.exit_button = tk.Button(input_frame, text="Exit", font="Helvetica 14 bold", bg="grey", fg="white", width=10, command=lambda: cg.close_game(self.window_game))
    self.exit_button.grid(row=2, column=1, padx=(0, 5), pady=(0, 30), sticky="n")
    #self.exit_button.grid_remove()
    self.exit_button.grid()
  '''
  # Pulsante di riavvio (inizialmente nascosto)
    self.restart_button = tk.Button(input_frame, text="Restart", font="Helvetica 14 bold", bg="grey", fg="white", width=10, command=self.restart_game)
    self.restart_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 30), sticky="n")
    self.restart_button.grid_remove()
    #self.restart_button.grid()
  '''

  def change_text(self):
      glvar.text_button="Enter"
      self.submit_button.config(text=glvar.text_button)  # Aggiorna il pulsante

  def run(self):
      self.window_game.mainloop()
  
  def displayFirst_message(self):
      self.phrase=sp.build_phrase_complete("I", "be", "Lara Croft")
      u.simulate_typing(self.chat_history, "Lara: "+ "Hi! " + self.phrase + "\n", tag="lara", submit_button=self.submit_button, user_input=self.user_input)

  def mng_user_input(self):
      user_message = self.user_input.get().strip()
                
      if user_message!='' and glvar.state_dialog>=0:
         u.simulate_typing(self.chat_history, "Player: "+ user_message + "\n", tag="player", submit_button=self.submit_button, user_input=self.user_input)
         print(user_message)
         self.chat_history.after(2000, lambda: self.process_bot_response(user_message))  
      else: 
         if glvar.text_button=='Enter':
            u.simulate_typing(
                self.chat_history,
                "Player:\n",
                tag="player",
                submit_button=self.submit_button,
                user_input=self.user_input
            )
         self.change_text()
         l.mng_dialog(user_message, self.chat_history, submit_button=self.submit_button, user_input=self.user_input)  # Ottieni la risposta
      
     
  def process_bot_response(self, user_message):
      l.mng_dialog(user_message, self.chat_history, submit_button=self.submit_button, user_input=self.user_input)  # Ottieni la risposta
  
  def show_end_buttons(self):
    #self.exit_button.grid()
    #self.restart_button.grid()
    self.submit_button.config(state='disabled')
    self.user_input.config(state='disabled')
  '''
  def restart_game(self):
    glvar.reset()  # Reset di tutte le variabili globali in una condizione di inizio gioco
    glvar.gui=self
    self.chat_history.delete('1.0', tk.END)
    self.user_input.config(state='normal')
    self.submit_button.config(state='normal')
    #self.exit_button.grid_remove()
    self.restart_button.grid_remove()
    
    # Ripristina testo del pulsante
    glvar.text_button = "Start chat"
    self.submit_button.config(text=glvar.text_button)

    # Mostra il messaggio iniziale
    self.window_game.after(500, self.displayFirst_message)

  
  def displayFirst_message(self):
    self.phrase = sp.build_phrase_complete("I", "be", "Lara Croft")
    u.simulate_typing(
        self.chat_history,
        "Lara: Hi! " + self.phrase + "\n", 
        tag="lara",
        submit_button=self.submit_button,
        user_input=self.user_input
    )
'''
  def load_image_with_black_background(self, filepath, size=None):
    image = Image.open(filepath).convert("RGBA")

    # Elimina pixel quasi trasparenti per il bounding box (ritaglio)
    alpha = image.split()[-1]  # canale alpha
    bbox = alpha.point(lambda p: p > 10 and 255).getbbox()  # soglia trasparenza = 10

    if bbox:
        image = image.crop(bbox)

    # Sovrapponi su sfondo nero
    black_bg = Image.new("RGBA", image.size, (0, 0, 0, 255))
    image = Image.alpha_composite(black_bg, image)

    # Ridimensiona se specificato
    if size:
        image = image.resize(size)

    # Converti in RGB (senza trasparenza) per Tkinter
    image_rgb = image.convert("RGB")
    self.image = ImageTk.PhotoImage(image_rgb)

