# main.py
import os
os.environ["NOMIC_DISABLE_TELEMETRY"] = "1"
from colorama import init, Fore

init(autoreset=True)


from rag_utils import (
    get_prompt_template,
    load_documents,
    configure_models,
    parse_documents,
    setup_vector_store,
    build_index,
    build_query_engine
)

def main():
    # Setup iniziale
    prompt_template = get_prompt_template()
    documents = load_documents()
    configure_models()
    parsed_nodes = parse_documents(documents)
    vector_store = setup_vector_store()
    index = build_index(parsed_nodes, vector_store)
    query_engine, retriever = build_query_engine(index, prompt_template)

    print(Fore.GREEN +"\nSystem ready. Type your question or enter 'exit' to quit.\n")

    while True:
        user_input = input(Fore.GREEN +"Question: ")
        if user_input.lower() in ("exit", "quit"):
            print(Fore.GREEN +"Good bye! See you next time")
            break

        try:
          retrieved_nodes = retriever.retrieve(user_input)
          print(f"\n  Nodi recuperati per la query: '{user_input}'")
          for i, node in enumerate(retrieved_nodes):
              print(f"\n--- Chunk {i + 1} ---")
              print(node.get_content())
              print(f"Score (similarità): {node.score}")
          response = query_engine.query(user_input)
          print("\n Answer:")
          print(Fore.GREEN + response)
        except Exception as e:
            print(f"Error during response generation: {e}")

if __name__ == "__main__":
    main()
