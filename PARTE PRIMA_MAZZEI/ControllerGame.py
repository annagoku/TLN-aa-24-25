import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
import WindowCredit as wc
import StartWindow as sw
import tkinter.messagebox as tm
import simpleNLG as sp
import time
import config as glvar
from ChatBotGui import ChatBotGui



#open window credit
def print_credit():
  wc.init_gui_credit()

def close_game(window):
  #quit()
  window.destroy()
  sw.init_gui()

def exitApplication(windows_root):
    
     # Se non è un gioco appena avviato
    MsgBox = tk.messagebox.askquestion('Exit Application', 'Sei sicuro di voler abbandonare il gioco?', icon='warning')
    if MsgBox == 'yes':
        windows_root.destroy()
    else:
        tk.messagebox.showinfo('Return', 'Sarai reindirizzato alla pagina principale')
   

def start_new_game(start_window):
    
     # Impostiamo il flag per il nuovo gioco
    glvar.is_start_game = True
    
    # Disattiva la chiusura "standard"
    start_window.protocol("WM_DELETE_WINDOW", lambda: None)

    start_window.destroy()
    app = ChatBotGui()
    glvar.gui=app
    app.run()




    
   
   
        