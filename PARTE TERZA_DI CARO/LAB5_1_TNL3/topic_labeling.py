from rich import print
import time



def etichetta_topic_interattivo(topic_model, pipe, topic_id, num_keywords=10, num_docs=3):
 

    # Estrai le keywords del topic
    topic_keywords = topic_model.get_topic(topic_id)[:num_keywords]
    keywords = [kw for kw, _ in topic_keywords]
    
    # Estrai gli abstracts più rappresentativi
    topic_docs = topic_model.get_representative_docs()[topic_id][:num_docs]

    print(f"\n[bold green]Topic {topic_id}[/bold green]")
    print(f"[bold yellow]Parole chiave:[/bold yellow] {', '.join(keywords)}\n")
    print("[bold cyan]Abstract rappresentativi:[/bold cyan]")
    for i, doc in enumerate(topic_docs):
        print(f"{i+1}. {doc[:200]}...")  # stampa i primi 200 caratteri

    print("\nOra puoi iterare e modificare il prompt finché non sei soddisfatto.\n")

    while True:
        prompt = input("👉 Inserisci un prompt per generare la label (o 'exit' per uscire):\n> ")
        if prompt.lower() in {"exit", "esci", "fine"}:
            break

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        print("\n⏳ Generazione in corso...")
        output = pipe(messages)
        label = output[0]["generated_text"].strip()
        
        print(f"\n[bold magenta]Etichetta generata:[/bold magenta] {label}\n")
