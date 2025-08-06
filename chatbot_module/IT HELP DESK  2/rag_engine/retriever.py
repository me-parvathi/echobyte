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
db = FAISS.load_local("rag_engine/vector_store", embeddings, allow_dangerous_deserialization=True)

# Setup LLM for answering questions
llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    model_name="gpt-4",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Load a QA chain
qa_chain = load_qa_chain(llm, chain_type="stuff")

# Get top k documents (raw retrieval)
def get_top_k_docs(query, k=2):
    return db.similarity_search(query, k=k)

# Get a full GPT-generated answer based on top-k docs (for chatbot integration)
def get_rag_response(query, k=2):
    docs = get_top_k_docs(query, k)
    if not docs:
        return "I'm sorry, I couldn't find anything related to that."
    return qa_chain.run(input_documents=docs, question=query)

# Optional testing
if __name__ == "__main__":
    query = input("Enter your query: ")
    response = get_rag_response(query)
    print(f"\nResponse:\n{response}")
