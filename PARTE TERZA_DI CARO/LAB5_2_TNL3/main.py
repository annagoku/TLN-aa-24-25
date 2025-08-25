import torch
from rich import print
import utility as u
import word_guessing as wg
import utility as u

FILE='dataset_definizioni_TLN_25.csv'

if __name__ == "__main__":
    
    print(" Verifica disponibilità CUDA...")
    print("CUDA disponibile:", torch.cuda.is_available())

    print("Creazione del model")
    model =wg.model_creation()

    print("Creazione del tokenizer")
    tokenizer =wg.tokenizer_creation()
    print("Creazione della pipe")
    pipe = wg.pipe_creation(model, tokenizer)
    
    print("Creazione dizionario")
    definizioni=u.load_data_dict()
    #print("Dizionario: ",definizioni)
    result, interaction_log=wg.interactive_guessing(definizioni,pipe)
    print(interaction_log)
    unified_result=u.unify_results_and_log(result, interaction_log)
    print(unified_result)

