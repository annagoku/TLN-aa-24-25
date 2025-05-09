import tkinter as tk
import pygame as py
from PIL import Image, ImageTk 
import ControllerGame as cg
import StartWindow as sw
from ChatBotGui import ChatBotGui
import simpleNLG as sp
import config as glvar


if __name__ == "__main__":
    app = ChatBotGui()
    glvar.gui=app
    app.run()
    

  

