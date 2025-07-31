import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from bertopic import BERTopic
from rich import print
import utility as u
import word_guessing as wg
import utility as u

FILE='dataset_definizioni_TLN_25.csv'

if __name__ == "__main__":
    
    print(" Verifica disponibilità CUDA...")
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

    
    definizioni=u.create_dictionary()
    print("Creazione dizionario: ",definizioni)
    result, interaction_log=wg.interactive_guessing(definizioni,pipe)
    #print(result)
    print(interaction_log)
    unified_result=u.unify_results_and_log(result, interaction_log)
    print(unified_result)