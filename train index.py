# train.py - Script to train the model on provided PDF files
import os
import pickle
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def train_model(pdf_files):
    """
    Train the model using the provided PDF files by loading them,
    embedding the documents, and storing them in a vector store.
    """
    if not pdf_files:
        print("No PDF files provided for training.")
        return None

    documents = []
    for file_path in pdf_files:
        if os.path.exists(file_path):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        else:
            print(f"File not found: {file_path}")

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save the trained vectorstore to a file for future use
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)

    print("Model trained and saved as vectorstore.pkl.")

def load_model():
    """
    Load the trained model from a pickle file.
    """
    try:
        with open("vectorstore.pkl", "rb") as f:
            vectorstore = pickle.load(f)
        return vectorstore
    except FileNotFoundError:
        print("No trained model found. Please train the model first.")
        return None


