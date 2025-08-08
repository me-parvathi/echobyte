import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain.chains.question_answering import load_qa_chain

# Load environment variables
load_dotenv()

# Set up Azure OpenAI embeddings
embeddings = AzureOpenAIEmbeddings(
    deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    model="text-embedding-ada-002",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Load FAISS vector store
try:
    db = FAISS.load_local("core/rag_engine/vector_store", embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Warning: Could not load FAISS vector store: {e}")
    db = None

# Setup LLM for answering questions
try:
    llm = AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        model_name="gpt-4",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    # Load a QA chain
    qa_chain = load_qa_chain(llm, chain_type="stuff")
except Exception as e:
    print(f"Warning: Could not initialize Azure OpenAI LLM: {e}")
    llm = None
    qa_chain = None

def get_top_k_docs(query: str, k: int = 2):
    """Get top k documents from vector store."""
    if not db:
        return []
    try:
        return db.similarity_search(query, k=k)
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return []

def get_rag_response(query: str, k: int = 2) -> str:
    """Get a full GPT-generated answer based on top-k docs."""
    if not db or not qa_chain:
        return "I'm sorry, I couldn't find anything related to that. The knowledge base is currently unavailable."
    
    try:
        docs = get_top_k_docs(query, k)
        if not docs:
            return "I'm sorry, I couldn't find anything related to that."
        return qa_chain.run(input_documents=docs, question=query)
    except Exception as e:
        print(f"Error in RAG response generation: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again."

def get_relevant_context(query: str, top_k: int = 3) -> str:
    """Get relevant context for backward compatibility with existing code."""
    if not db:
        return ""
    
    try:
        docs = get_top_k_docs(query, top_k)
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"Error getting relevant context: {e}")
        return ""

# For testing
if __name__ == "__main__":
    query = input("Enter your query: ")
    response = get_rag_response(query)
    print(f"\nResponse:\n{response}")
