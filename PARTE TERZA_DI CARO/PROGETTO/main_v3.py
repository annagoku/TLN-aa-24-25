from retrieve import load_or_create_index, retrieve, generate_answer

# Percorso del file sorgente
FILE_PATH = "cat-facts.txt"

# Inizializzazione
text_db, faiss_index = load_or_create_index(FILE_PATH)

print("Benvenuto nel Chatbot Etologo dei Gatti!")
print("Digita 'exit' per terminare.\n")

# Ciclo principale
while True:
    user_input = input("Fai una domanda o digita 'exit': ").strip()
    if user_input.lower() in ['exit', 'quit']:
        print("👋 Ciao! Alla prossima.")
        break

    retrieved_knowledge = retrieve(user_input, text_db, faiss_index)
    print("\n🔍 Frammenti recuperati:")
    for chunk, score in retrieved_knowledge:
        print(f" - ({1/(1+score):.2f}) {chunk.strip()}")

    print("\n💬 Risposta del modello:")
    stream = generate_answer(user_input, retrieved_knowledge)
    for part in stream:
        print(part['message']['content'], end='', flush=True)
    print("\n")




