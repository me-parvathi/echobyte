import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./core/rag_engine/chroma_store")
collection = client.get_collection("helpdesk_docs")

def get_relevant_context(query, top_k=3):
    embedding = model.encode([query]).tolist()[0]
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    return "\n\n".join(results["documents"][0])

# For testing
if __name__ == "__main__":
    context = get_relevant_context("How long does a high priority ticket take?")
    print(context)
