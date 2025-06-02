import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
import ControllerGame as cg

  # modale credits
def init_gui_credit():
  windows_credit=tk.Toplevel()
  window_height = 500
  window_width = 600
  windows_credit.title("Tomb Raider Challenge @Credits")
  windows_credit.resizable(False,False)
  windows_credit.configure(bg="white")

  screen_width = windows_credit.winfo_screenwidth()
  screen_height = windows_credit.winfo_screenheight()

  x_cordinate = int((screen_width/2) - (window_width/2))
  y_cordinate = int((screen_height/2) - (window_height/2))

  windows_credit.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
  
  text1="Author: Annalisa Sabatelli"
  text2=" Esame di Tecnologie del linguaggio naturale a.a. 2024/2025"
  credit_label1=tk.Label(windows_credit, text=text1, fg="black", bg="white", font="Helvetica 14")
  credit_label1.pack( pady=30, side=tk.TOP)
  credit_label2=tk.Label(windows_credit, text=text2, fg="black", bg="white", font="Helvetica 14 bold")
  credit_label2.pack(  side=tk.TOP)

  image = ImageTk.PhotoImage(Image.open('logo_ufficiale_web.jpg'))
  bg_label = tk.Label(windows_credit, image = image)
  bg_label.pack(pady=40,side=tk.TOP)
  bg_label.image = image

  exit_button=tk.Button(windows_credit, text="Close",background="darkblue", fg="white", font="Helvetica 12 bold", height=1, width=7, command=windows_credit.destroy)
  exit_button.pack(padx=100,pady=20, side=tk.BOTTOM)