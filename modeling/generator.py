from transformers import pipeline

class Generator:
    def __init__(self, model_name="t5-small"):
        self.model = pipeline("text2text-generation", model=model_name)

    def generate(self, context, question):
        input_text = f"Context: {context} Question: {question}"
        response = self.model(input_text)
        return response[0]["generated_text"]
