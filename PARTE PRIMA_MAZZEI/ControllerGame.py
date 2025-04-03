import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
import WindowCredit as wc
import StartWindow as sw
import tkinter.messagebox as tm
import simpleNLG as sp
import time



#open window credit
def print_credit():
  wc.init_gui_credit()

def close_game():
  quit()

def exitApplication(windows_root):
  MsgBox = tk.messagebox.askquestion ('Exit Application','Sei sicuro di voler abbandonare il gioco?',icon = 'warning')
  if MsgBox == 'yes':
      windows_root.destroy()
  else:
      tk.messagebox.showinfo('Return','Sarai reindirizzato alla pagina principale')


   



    
   
   
        