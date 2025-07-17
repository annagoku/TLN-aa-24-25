import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from bertopic import BERTopic
import topic_labeling as tl



if __name__ == "__main__":
    #res = torch.cuda.is_available()
    #print("CUDA available:", res)

    model_path = "./my_llm_model"
    tokenizer_path = "./my_llm_tokenizer"
    topic_model_path="../LAB4_TNL3/topic_model"

    # Controlla se il modello e tokenizer sono già salvati
    if os.path.exists(model_path) and os.path.exists(tokenizer_path):
        print("Caricamento modello e tokenizer da disco...")
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    else:
        print("Scaricamento e salvataggio modello e tokenizer...")
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Phi-3.5-mini-instruct",
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=False
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/Phi-3.5-mini-instruct",
            trust_remote_code=True
        )
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(tokenizer_path)

    # Creazione pipeline di generazione
    print("Creazione pipe")
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300
    )

    #Carica il topic model
    print("Carcamento topic model")
    topic_model=BERTopic.load(topic_model_path)
    # Definizione del prompt
    # Itera su tutti i topic tranne -1 (rumore/outlier)
    topic_info = topic_model.get_topic_info()
    for topic_id in topic_info['Topic']:
        if topic_id == -1:
            continue
        print(f"\n=== Iterazione su Topic ID: {topic_id} ===")
        tl.etichetta_topic_interattivo(topic_model, pipe, topic_id)
