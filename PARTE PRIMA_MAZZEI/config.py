player_name=''
player_id=''
started=False
text_button='Start chat'
state_dialog=-1 #valori ammissibili default Intro-->-1, 0-->Nome, 1-->Preparazione, 2-->Prima Domanda, 3-->Seconda domanda, 4-->Terza domanda, 10-->Exit
punteggio=0  #+1 per ogni domanda corretta
questions_made=[]
is_typing=False
pending_message = None
pending_chat_history = None
end_game=False
gui= None
#is_start_game=True

#Modellare un sistema a stati finiti

def reset():
  global player_name, player_id, started, text_button, state_dialog, punteggio
  global questions_made, is_typing, pending_message, pending_chat_history
  global end_game, gui

  player_name=''
  player_id=''
  started=False
  text_button='Start chat'
  state_dialog=-1 
  punteggio=0 
  questions_made=[]
  is_typing=False
  pending_message = None
  pending_chat_history = None
  end_game=False
  gui= None
  