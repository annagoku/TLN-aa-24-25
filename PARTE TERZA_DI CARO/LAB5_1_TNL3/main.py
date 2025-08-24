import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from bertopic import BERTopic
import topic_labeling as tl
import topic_modeling_lab5 as tm
from rich import print
import os

topic_model_path="topic_model"

if __name__ == "__main__":
    print(" Verifica disponibilità CUDA...")
    print("CUDA disponibile:", torch.cuda.is_available())

#Recupero topic model sulla base del dataset del laboratorio 4
    if os.path.exists(topic_model_path):
       print("Caricamento topic model già esistente...")
       topic_model = BERTopic.load(topic_model_path)
       
    else:
       print("Creazione di un nuovo topic model...")
       topic_model=tm.topic_modeling_creation()
       print("Salvataggio del topic model...")
       topic_model.save(topic_model_path)

    print("Caricamento del model")
    model = tl.model_creation()

    print("Caricamento del tokenizer")
    tokenizer = tl.tokenizer_creation()

    print("Creazione della pipe")
    pipe =tl.pipe_creation(model, tokenizer)

    results=tl.label_all_topics(topic_model,pipe)
    print(results)
  
    