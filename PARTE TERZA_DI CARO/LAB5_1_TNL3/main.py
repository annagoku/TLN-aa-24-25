import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from bertopic import BERTopic
import topic_labeling as tl
from rich import print

if __name__ == "__main__":
    print("🚀 Verifica disponibilità CUDA...")
    print("CUDA disponibile:", torch.cuda.is_available())

    tokenizer_path = "./my_llm_tokenizer"
    topic_model_path="../LAB4_TNL3/topic_model"


    
    # Caricamento modello direttamente, senza salvarlo
    print("🔧 Caricamento modello LLM...")
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Phi-3.5-mini-instruct",
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=False
    )
  

    # Caricamento tokenizer
    if os.path.exists(tokenizer_path):
        print("✅ Caricamento tokenizer da disco...")
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    else:
        print("⬇️ Scaricamento tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/Phi-3.5-mini-instruct",
            trust_remote_code=True
        )
        tokenizer.save_pretrained(tokenizer_path)
        print("💾 Tokenizer salvato.")


    # Creazione della pipeline di generazione
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300
    )

    # Caricamento del modello di topic
    print("📦 Caricamento BERTopic model...")
    topic_model = BERTopic.load(topic_model_path)


    # Iterazione sui topic per assegnare etichette
    for topic_id in topic_model.get_topics().keys():
        if topic_id == -1:
            continue  # salta il topic -1 (outlier)
        tl.etichetta_topic_interattivo(topic_model, pipe, topic_id)
