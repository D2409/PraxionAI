from flask import Flask, request, jsonify
from rag_pipeline import RAGPipeline

app = Flask(__name__)
rag = RAGPipeline()

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data["question"]
    documents = data["documents"]
    answer = rag.answer_question(question, documents)
    return jsonify({"answer": answer})
