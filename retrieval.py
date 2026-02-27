from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from loguru import logger

from data import load_csv

logger.add("log/retrieval.log")

load_dotenv()

query_engine = None
index_initialized = False


def build_index():
    """Build and cache vector index with error handling"""
    global query_engine, index_initialized

    try:
        logger.info("Starting vector index build...")
        df = load_csv()
        docs = [Document(text=row["text"]) for _, row in df.iterrows()]
        logger.info(f"Creating embeddings for {len(docs)} documents ...")
        index = VectorStoreIndex.from_documents(docs)
        logger.info("Vector index built successfully")

        # initialize llm and query engine
        llm = GoogleGenAI(model="gemini-2.5-flash", temperature=0.2)
        _ = GoogleGenAIEmbedding(model="text-embedding-004")
        query_engine = index.as_query_engine(llm=llm, similarity_top_k=2)
        index_initialized = True
        return query_engine
    except Exception as e:
        logger.error(f"Error building index: {str(e)}")
        index_initialized = False
        return None


def initialized_retrieval():
    """Initialize retrieval system on startup"""
    global query_engine, index_initialized
    try:
        logger.info("Initializing retrieval system...")
        query_engine = build_index()
        if query_engine:
            logger.info("Retrieval system initialized successfully")
        else:
            logger.warning("Retrieval system initialization failed - queries may fail")
            index_initialized = False
    except Exception as e:
        logger.error(f"Failed to initialize retrieval : {str(e)}")
        index_initialized = False


def execute_query(question: str) -> str:
    """Execute a query using the query engine

    Args:
        question (str): _description_

    Returns:
        str: _description_
    """
    if query_engine is None:
        raise Exception("Query engine is not initialized")

    try:
        response = query_engine.query(question)
        return str(response)
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise
