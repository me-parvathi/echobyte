import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load .env
load_dotenv()

def create_vector_store():
    """Create FAISS vector store from helpdesk documents."""
    
    # Check if documents exist
    docs_path = "./core/rag_engine/docs/helpdesk_faq.txt"
    if not os.path.exists(docs_path):
        print(f"❌ Document not found: {docs_path}")
        return False
    
    try:
        # Load and split the document
        loader = TextLoader(docs_path, encoding="utf-8")
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
        docs = text_splitter.split_documents(documents)

        print(f"✅ Loaded {len(docs)} document chunks")

        # Initialize embedding model
        embeddings = AzureOpenAIEmbeddings(
            deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            model="text-embedding-ada-002",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )

        print("✅ Embeddings model initialized")

        # Create and save vector store
        db = FAISS.from_documents(docs, embeddings)
        db.save_local("core/rag_engine/vector_store")
        print("✅ Vector store created successfully at core/rag_engine/vector_store")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting vector store creation...")
    success = create_vector_store()
    if success:
        print("🎉 Vector store creation completed successfully!")
    else:
        print("💥 Vector store creation failed!")
