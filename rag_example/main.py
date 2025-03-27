from corpus import corpus_of_documents
from retriever import retrieve_document
from rag_system import generate_response

def main():
    print("Welcome to the Activity Recommendation System!")
    while True:
        try:
            # Get user input
            user_input = input("\nEnter your activity preference (or 'quit' to exit): ").strip()
            if user_input.lower() == 'quit':
                print("\nThank you for using the system. Goodbye!")
                break

            # Step 1: Retrieve the most relevant document
            relevant_document = retrieve_document(user_input, corpus_of_documents)
            print(f"\nRetrieved Document: {relevant_document}")

            # Step 2: Generate a response using OpenAI GPT
            bot_response = generate_response(user_input, relevant_document)
            print(f"Bot Recommendation: {bot_response}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
