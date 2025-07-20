from rich import print
import torch


def label_all_topics(topic_model, pipe, num_keywords=10, num_docs=3):
    results = []
    topic_num=len(topic_model.get_topics())-1
    print("Numero totale di topic: ",topic_num)
    count=0
    for topic_id in topic_model.get_topics():
        if topic_id == -1:
            continue

        if count >= 3:
            break

        topic_keywords = topic_model.get_topic(topic_id)[:num_keywords]
        keywords = [kw for kw, _ in topic_keywords]
        topic_docs = topic_model.get_representative_docs()[topic_id][:num_docs]

        print(f"\n[Topic {topic_id}]")
        print(f" Keywords: {', '.join(keywords)}\n")

        print(" Representative abstracts:")
        for i, doc in enumerate(topic_docs):
            print(f"{i+1}. {doc[:200]}...")

        final_label = None
        count += 1

        # Prepara le keyword solo per il primo prompt
        keyword_string = f"Keywords: {', '.join(keywords)}"
        conversation_history = []  # lista dei messaggi da mantenere
        first_iteration = True

        while True:
            prompt = input(
                "\n Enter a custom prompt to generate the label (or type 'exit' to quit):\n> "
            ).strip()

            if prompt.lower() == "exit":
                return results

            if not prompt:
                print(" Invalid prompt. Please try again.")
                continue

            if first_iteration:
                full_prompt = f"{prompt} {keyword_string}"
                first_iteration = False
            else:
                full_prompt = prompt

            # Aggiungi il nuovo messaggio alla conversazione
            conversation_history.append({"role": "user", "content": full_prompt})

            print(f"\n Final prompt:\n{full_prompt}")
            print(" Generating label...")

            try:
                output = pipe(conversation_history)
                print(output)

                # Estrai risposta dell'assistente
                if isinstance(output[0]["generated_text"], str):
                    full_text = output[0]["generated_text"]
                elif isinstance(output[0]["generated_text"], list):
                    # Cerca l'ULTIMO messaggio con ruolo "assistant"
                    assistant_messages = [msg.get("content", "") for msg in output[0]["generated_text"] if msg.get("role") == "assistant"]
                    if assistant_messages:
                        full_text = assistant_messages[-1]  # prende l'ultimo
                    else:
                        full_text = ""
                else:
                    raise ValueError("Unexpected output format from pipeline.")

                label = full_text.strip()
                print(f"\n Generated label: {label}")

                # Aggiungi anche la risposta alla history
                conversation_history.append({"role": "assistant", "content": label})

                satisfied = input(" Are you satisfied with this label? (y/n): ").strip().lower()
                if satisfied == "y":
                    final_label = label
                    break
                else:
                    print(" Try again with a new prompt.")

            except Exception as e:
                print(f" Error during generation: {e}")

        results.append({
            "topic_id": topic_id,
            "keywords": keywords,
            "label": final_label
        })

    return results
