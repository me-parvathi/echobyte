import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load .env
load_dotenv()

# Load and split the document
loader = TextLoader("./docs/helpdesk_faq.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
docs = text_splitter.split_documents(documents)

# Print deployment to debug
print("Using deployment:", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"))
print("Using API key:", os.getenv("AZURE_OPENAI_API_KEY"))   
print("Using API base:", os.getenv("AZURE_OPENAI_ENDPOINT"))


# Initialize embedding model with correct fields
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

print("Using deployment:", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"))
print("Using API key:", os.getenv("AZURE_OPENAI_API_KEY"))   
print("Using API base:", os.getenv("AZURE_OPENAI_ENDPOINT"))

# Create and save vector store
db = FAISS.from_documents(docs, embeddings)
db.save_local("vector_store")
print("✅ Vector store created successfully.")
