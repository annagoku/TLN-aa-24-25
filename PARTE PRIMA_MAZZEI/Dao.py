from pymongo import MongoClient
import config as glvar



def save_name(player_name):
     try:
        # Connessione a MongoDB in Docker
        client = MongoClient("mongodb://admin:secret@localhost:27017/")

        # Controlla che il database esista
        #print("Database disponibili: ", client.list_database_names())
        
        #Seleziona il database e la collezione
        db = client["Lara_challange"]
        collection = db["Player"]

        # Dati da salvare
        name = {"name": player_name}

        # Inserimento nel database
        result=collection.insert_one(name)

        #Recupero dell'ID del database per il documento inserito

        glvar.player_id=result.inserted_id

        # Chiude la connessione
        client.close()

        #print("Nome salvato con successo! ID: " +  str(result.inserted_id))
    
     except Exception as e:
        print ("Errore durante il salvataggio: "+ str(e))


def retrieve_question_by_code(random_code):
    try:
     # Connessione a MongoDB in Docker
        client = MongoClient("mongodb://admin:secret@localhost:27017/")

        # Controlla che il database esista
        #print("Database disponibili: ", client.list_database_names())
        
        #Seleziona il database e la collezione
        db = client["Lara_challange"]
        collection = db["Questions"]


        # Cerca un elemento con la chiave specificata
        query = {"code": random_code}
        result = collection.find_one(query)

        if result:
            return result

        # Chiude la connessione
        client.close()

    except Exception as e:
        print("Errore durante la ricerca:", str(e))
        return None


def save_question_made_for_player(random_code):
    try:
     # Connessione a MongoDB in Docker
        client = MongoClient("mongodb://admin:secret@localhost:27017/")
        
        #Seleziona il database e la collezione
        db = client["Lara_challange"]
        collection = db["Player"]

        # Dati da salvare
        query={"_id": glvar.player_id }
       # Aggiornamento per aggiungere il campo "question_list_code"
        update = {"$push": {"question_list_code": random_code}}

        # Esegui l'aggiornamento
        collection.update_one(query, update)

        # Chiude la connessione
        client.close()

    except Exception as e:
        print("Errore durante la ricerca:", str(e))


def save_answer_player(user_message, num_question):
    try:
     # Connessione a MongoDB in Docker
        client = MongoClient("mongodb://admin:secret@localhost:27017/")
        
        #Seleziona il database e la collezione
        db = client["Lara_challange"]
        collection = db["Player"]
        
        # Dati da salvare
        query={"_id": glvar.player_id }
        # Dati da salvare
        answer = "Question " + str(num_question)+": "+ user_message

        # Aggiornamento per aggiungere il campo "question_list_code"
        update = {"$push": {"question_answer": answer}}

        # Inserimento nel database
        # Esegui l'aggiornamento
        collection.update_one(query, update)

        # Chiude la connessione
        client.close()

    except Exception as e:
        print("Errore durante la ricerca:", str(e))

def save_correct_answer_for_player(correct_answer, num_question):
    try:
     # Connessione a MongoDB in Docker
        client = MongoClient("mongodb://admin:secret@localhost:27017/")
        
        #Seleziona il database e la collezione
        db = client["Lara_challange"]
        collection = db["Player"]
        
        # Dati da salvare
        query={"_id": glvar.player_id }

        # Se correct_answer è una lista, uniscila in una stringa
        if isinstance(correct_answer, list):
            answer_str = ", ".join(map(str, correct_answer))
        else:
            answer_str = str(correct_answer)

        # Dati da salvare
        answer = f"Question {num_question} correct answer: {answer_str}"

        # Aggiornamento per aggiungere il campo "question_list_code"
        update = {"$push": {"question_correct_answer": answer}}

        # Inserimento nel database
        # Esegui l'aggiornamento
        collection.update_one(query, update)

        # Chiude la connessione
        client.close()

    except Exception as e:
        print("Errore durante la ricerca:", str(e))



def update_point_for_player(point):
    try:
     # Connessione a MongoDB in Docker
        client = MongoClient("mongodb://admin:secret@localhost:27017/")

        #Seleziona il database e la collezione
        db = client["Lara_challange"]
        collection = db["Player"]

        # Dati da salvare
        query={"_id": glvar.player_id }
      # Aggiornamento: se "point" esiste, lo incrementa; altrimenti, lo crea con il valore specificato
        update = {"$set":{"player total points":point}}

        # Esegui l'aggiornamento, senza creare un nuovo documento se non esiste
        collection.update_one(query, update, upsert=False)

        # Chiude la connessione
        client.close()

    except Exception as e:
        print("Errore durante la ricerca:", str(e))