from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser, SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, StorageContext, ServiceContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.settings import Settings
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.prompts import PromptTemplate
import chromadb


custom_prompt_str = """
    You are an experienced riding instructor, skilled in training, equine ethology, and horse anatomy.
    The context provided will be about horse and it is taken from Horsemanship manual.
    Answer the question **strictly using the context below** and include any **relevant facts** you find only in the context. Be concise but informative.
    Don't add comments or information not included in the context.
    **IMPORTANT** if the context doesn't contain useful information for the answer, say that you are not able to answer."

CONTEXT:
{context_str}

QUESTION:
{query_str}

ANSWER:
"""

# 0. Prompt template corretto
custom_prompt = PromptTemplate(custom_prompt_str)

# 1. Carica i documenti
print("Carica i documenti")
documents = SimpleDirectoryReader(input_dir="data").load_data()

# 2. Configura LLM + embedding (solo Ollama)
print("Configura i modelli di embedding e generazione")
Settings.llm = Ollama(model="mistral:7b-instruct-q4_0", request_timeout=120)
Settings.embed_model = OllamaEmbedding(model_name="all-minilm")


# 3. Chunking con SemanticSplitterNodeParser (serve embed_model obbligatorio)
print("Creazione dei chunck")
'''
node_parser = SemanticSplitterNodeParser(
    buffer_size=64,
    embed_model=Settings.embed_model,
    include_prev_next_rel=False,
    include_metadata=False
)
'''

node_parser = SentenceSplitter(
    chunk_size=512,          # lunghezza in token
    chunk_overlap=50,        # sovrapposizione per mantenere contesto
    paragraph_separator="\n\n",
    include_metadata=True,
    include_prev_next_rel=False  # disattiva relazioni semantiche
)

parsed_nodes = node_parser.get_nodes_from_documents(documents)

# 4. Configura Chroma Vector Store persistente
print("Configurazione chroma")
chroma_client = chromadb.PersistentClient(path="./storage")
chroma_collection = chroma_client.get_or_create_collection("rag_collection")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 5. Costruisci StorageContext e indice usando i nodes chunkati
print("Indicizzazione e salvataggio chunk creati")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
'''
service_context=ServiceContext.from_defaults(
    llm=Settings.llm,
    embed_model=Settings.embed_model
)
'''
vector_index = VectorStoreIndex.from_documents(parsed_nodes, storage_context=storage_context)

# Persisti il vector store
vector_index.storage_context.vector_store.persist(persist_path="./chroma_db")

# 6. Crea retriever e query engine con top_k e cutoff
top_k = 5
#cutoff = 0.5

''''
index_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=top_k)
print("Creazione del motore di retrivial")
retriever = RetrieverQueryEngine(
    retriever=index_retriever,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=cutoff)],
)
'''
print("Creazione del motore di ricerca")
retriever= vector_index.as_retriever(top_k=top_k)
synthesizer = get_response_synthesizer(
    response_mode="refine",  # o "generation", "refine", ecc.
    text_qa_template=custom_prompt
)  # migliora coerenza
#query_engine=RetrieverQueryEngine(retriever=retriever, response_synthesizer=synthesizer)
query_engine = RetrieverQueryEngine.from_args(retriever=retriever, response_synthesizer=synthesizer)

                                  
print("Esempio di query")
text="What about horse feeding? "
print(text)
retrieved_nodes = retriever.retrieve(text)

print(f"\n  Nodi recuperati per la query: '{text}'")
for i, node in enumerate(retrieved_nodes):
    print(f"\n--- Chunk {i + 1} ---")
    print(node.get_content())
    print(f"Score (similarità): {node.score}")

response = query_engine.query(text)

print("Risposta del modello: ", response)

