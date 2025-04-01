# import os
# import numpy as np
# import torch
# from sentence_transformers import SentenceTransformer, util

# # Load the sentence transformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Load the corpus from corpus.py
# from corpus import corpus_of_documents

# # Precompute embeddings once during app start
# corpus_embeddings = model.encode(corpus_of_documents, convert_to_tensor=True)

# def get_response(user_query, top_k=1):
#     """
#     Takes a user query, finds the most similar sentence(s) in the corpus,
#     and returns the most relevant response.
#     """
#     query_embedding = model.encode(user_query, convert_to_tensor=True)

#     # Compute cosine similarity between the query and the corpus
#     hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)
#     hits = hits[0]  # Only one query at a time

#     # Get the top result
#     top_match = hits[0]
#     best_index = top_match['corpus_id']
#     best_score = top_match['score']

#     best_sentence = corpus_of_documents[best_index]

    
#     print("\n🔍 User Query:", user_query)
#     print("🔍 Top Match:", best_sentence)
#     print("🔍 Similarity Score:", best_score)

#     # Add confidence threshold (e.g., 0.6)
#     """ 
#     if best_score < 0.6:
#         return "Sorry, I couldn't find a relevant answer." """

    


#     # Optional: Add a confidence check or formatting
#     return best_sentence

# from retriever import Retriever
# from generator import Generator
import os
from tqdm import tqdm
from pdf2image import convert_from_path
import pytesseract
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_ollama.llms import OllamaLLM

# Define the directory where your PDFs are stored
pdf_directory = "./policies"
documents = []

# Iterate over PDF files and perform OCR using pdf2image and pytesseract
for filename in tqdm(os.listdir(pdf_directory), desc="Processing PDFs"):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        try:
            # Convert PDF pages to images
            pages = convert_from_path(pdf_path)
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            continue
        
        for page_num, page in enumerate(pages, start=1):
            try:
                # Perform OCR on the image to extract text
                text = pytesseract.image_to_string(page)
                metadata = {"source": filename, "page": page_num}
                documents.append(Document(page_content=text, metadata=metadata))
            except Exception as e:
                print(f"Error processing page {page_num} of {filename}: {e}")

# Define a text splitter for chunking documents.
# Here we set a chunk size of 1000 characters with an overlap of 200 characters.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Split each document into chunks with a progress bar
chunked_documents = []
for doc in tqdm(documents, desc="Chunking documents"):
    chunks = text_splitter.split_text(doc.page_content)
    for chunk in chunks:
        chunked_documents.append(Document(page_content=chunk, metadata=doc.metadata))

# Instantiate the embeddings model using all‑MiniLM‑L6‑v2
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Define a directory to persist the Chroma DB vector store
persist_directory = "./chroma_db_policies"

# Create the vector store from the chunked documents using the HuggingFace embeddings
vectorstore = Chroma.from_documents(chunked_documents, embedding_model, persist_directory=persist_directory)
vectorstore.persist()

print("Embeddings generated and stored in Chroma DB using all‑MiniLM‑L6‑v2 HuggingFace Embeddings.")


# Instantiate the Ollama LLM (ensure your local Ollama server is accessible at the provided base_url)
llm = OllamaLLM(model="llama3.2", base_url="http://10.50.10.240:10023/")  

# Create a RetrievalQA chain using the vectorstore as the retriever
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
)

print("RetrievalQA chain is set up and ready for queries using Ollama LLM.")


#class RAGPipeline:
    # def __init__(self):
    #     self.retriever = Retriever()
    #     self.generator = Generator()

def get_response(question):
        # Retrieve relevant context
        # indices, _ = self.retriever.search(question)
        # context = " ".join([documents[i] for i in indices[0]])  # Combine top results
        
        # Generate answer
        #answer = self.generator.generate(context, question)
    answer = qa_chain.run(question)
    return answer
