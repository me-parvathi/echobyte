import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer

docs_path = "./rag_engine/docs"
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./rag_engine/chroma_store")
collection = client.create_collection("helpdesk_docs")

def load_docs():
    chunks = []
    for filepath in glob.glob(f"{docs_path}/*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            for para in text.split("\n\n"):
                if para.strip():
                    chunks.append(para.strip())
    return chunks

def main():
    docs = load_docs()
    embeddings = model.encode(docs).tolist()
    for i, doc in enumerate(docs):
        collection.add(documents=[doc], ids=[f"doc_{i}"], embeddings=[embeddings[i]])
    print("Embedding done.")

if __name__ == "__main__":
    main()
