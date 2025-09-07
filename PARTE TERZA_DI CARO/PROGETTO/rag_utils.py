from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser, SentenceSplitter
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.settings import Settings
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate
import chromadb


def get_prompt_template():
    custom_prompt_str = """
        You are an experienced riding instructor, skilled in training, equine ethology, and horse anatomy.
        The context provided will be about horse and it is taken from Horsemanship manual.
        Answer the question **strictly using the context below** and include any **relevant facts** you find only in the context. Be concise but informative.
        Don't add comments or information not included in the context.
        **IMPORTANT** if the context doesn't contain useful information for the answer, say that you are not able to answer.

    CONTEXT:
    {context_str}

    QUESTION:
    {query_str}

    ANSWER:
    """
    return PromptTemplate(custom_prompt_str)



def load_documents(data_path="data"):
    print("Caricamento documenti")
    return SimpleDirectoryReader(input_dir="data").load_data()


def configure_models():
    print("Configurazione LLM e modello di embedding")
    Settings.llm = Ollama(model="mistral:7b-instruct-q4_0", request_timeout=270)
    Settings.embed_model = OllamaEmbedding(model_name="all-minilm")


def parse_documents(documents):
    print("Suddivisione in chunk")
    parser = SentenceSplitter(
        chunk_size=400,
        chunk_overlap=50,
        paragraph_separator="\n\n",
        include_metadata=True,
        include_prev_next_rel=False
    )
    return parser.get_nodes_from_documents(documents)


def setup_vector_store():
    print("Creazione del vettore store persistente")
    chroma_client = chromadb.PersistentClient(path="./storage")
    chroma_collection = chroma_client.get_or_create_collection("rag_collection")
    return ChromaVectorStore(chroma_collection=chroma_collection)


def build_index(parsed_nodes, vector_store):
    print("Indicizzazione dei chunk")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(parsed_nodes, storage_context=storage_context)
    index.storage_context.vector_store.persist(persist_path="./chroma_db")
    return index


# --- RETRIEVAL ---
def build_retriever(index, top_k=5):
    """
    Costruisce la componente di retrieval a partire dall'indice.
    Restituisce un retriever che recupera i top_k chunk più rilevanti.
    """
    print("Creazione del retriever")
    retriever = index.as_retriever(top_k=top_k)
    return retriever


# --- GENERAZIONE ---
def build_generator(prompt_template, mode="refine"):
    """
    Costruisce la componente di generazione (synthesizer).
    response_mode='refine' permette di generare una prima risposta
    e raffinarla progressivamente con i chunk successivi.
    """
    print("Creazione del generatore di risposte")
    synthesizer = get_response_synthesizer(
        response_mode=mode,
        text_qa_template=prompt_template
    )
    return synthesizer

# --- QUERY ENGINE (retrieval + generazione) ---
def build_query_engine(index, prompt_template, top_k=5):
    """
    Integra retriever e generator in un unico motore di query.
    """
    retriever = build_retriever(index, top_k=top_k)
    synthesizer = build_generator(prompt_template, mode="refine")

    print("Creazione del motore di ricerca e generazione")
    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        response_synthesizer=synthesizer
    )
    return query_engine, retriever

