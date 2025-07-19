import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from bertopic import BERTopic
import topic_labeling as tl
from rich import print

topic_model_path="../LAB4_TNL3/topic_model"

if __name__ == "__main__":
    print("🚀 Verifica disponibilità CUDA...")
    print("CUDA disponibile:", torch.cuda.is_available())


    print("Creazione del model")
    model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=False
    )

    print("Creazione del tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/Phi-3.5-mini-instruct",
    trust_remote_code=True
    )
    print("Creazione della pipe")
    pipe = pipeline(
    "text-generation",
    model=model,
    max_new_tokens=300,
    tokenizer=tokenizer
    )

    
    print("📦 Caricamento BERTopic model...")
    topic_model = BERTopic.load(topic_model_path)

    results=tl.label_all_topics(topic_model,pipe)
    print(results)
  
    