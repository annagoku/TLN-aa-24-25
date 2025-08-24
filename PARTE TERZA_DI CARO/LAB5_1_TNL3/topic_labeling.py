from rich import print
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import topic_modeling_lab5 as tm
import utility as u
import random
import pickle



def model_creation():
    model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=False
    )
    return model

def tokenizer_creation():
    tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    trust_remote_code=True
    )
    return tokenizer

def pipe_creation(model, tokenizer):
    pipe = pipeline(
    "text-generation",
    model=model,
    max_new_tokens=300,
    tokenizer=tokenizer,
    temperature=0.2,
    top_p=1
    )
    return pipe


def label_all_topics(topic_model, pipe, num_keywords=10, num_docs=3):
    results = []
    topic_num=len(topic_model.get_topics())-1
    print("Numero totale di topic: ",topic_num)
    count=0
    topic_ids = [tid for tid in topic_model.get_topics().keys() if tid != -1]
    with open("mapping.pkl", "rb") as f:
            mapping = pickle.load(f)

    # Scelta di 3 topic a caso (senza ripetizioni)
    sampled_ids = random.sample(topic_ids, min(3, len(topic_ids)))
    print("Topic scelti:", sampled_ids)
    for topic_id in sampled_ids:
        if topic_id == -1:
            continue

        if count >= 3:
            break

        topic_keywords = topic_model.get_topic(topic_id)[:num_keywords]
        keywords = [kw for kw, _ in topic_keywords]
        topic_docs = topic_model.get_representative_docs()[topic_id][:num_docs]
        # Recupero abstract originali e titoli dal mapping
        original_docs_with_titles = [mapping.get(doc, (doc, "No Title")) for doc in topic_docs]

        print(f"\n[Topic {topic_id}]")
        print(f"{', '.join(keywords)}\n")

        print(" Representative abstracts:")
        for i, (orig_abstract, title) in enumerate(original_docs_with_titles):
            print(f"{i+1}. Title: {title}")
            print(f"   Abstract: {orig_abstract[:200]}...\n")

        final_label = None
        count += 1

        # Prepara le keyword solo per il primo prompt
        keyword_string = f" {', '.join(keywords)}"
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
