player_name=''
started=False
text_button='Start chat'
state_dialog=-1 #valori ammissibili default Intro-->-1, 0-->Nome, 1-->Preparazione, 2-->Prima Domanda, 3-->Seconda domanda, 4-->Terza domanda, 10-->Exit
punteggio=0  #+1 per ogni domanda corretta
questions_made=[]

#Modellare un sistema a stati finiti