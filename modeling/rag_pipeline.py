from retriever import Retriever
from generator import Generator

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    def answer_question(self, question, documents):
        # Retrieve relevant context
        indices, _ = self.retriever.search(question)
        context = " ".join([documents[i] for i in indices[0]])  # Combine top results
        
        # Generate answer
        answer = self.generator.generate(context, question)
        return answer
