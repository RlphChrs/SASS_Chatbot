from config import index, openai

# 🔹 Query chatbot for a specific school
def query_chatbot(school_id, user_input):
    # Convert user input to vector
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=user_input
    )
    query_vector = response.data[0].embedding

    # Search Pinecone for relevant text (filtered by school)
    search_results = index.query(
        vector=query_vector,  # Must use keyword argument
        top_k=3,
        filter={"school": school_id},  # Filter by school
        include_metadata=True
    )


    # Extract the most relevant text chunks
    retrieved_texts = "\n\n".join([match["metadata"]["text"] for match in search_results["matches"]])

    # Generate chatbot response
    chat_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are a chatbot for {school_id}. Use this knowledge:\n\n{retrieved_texts}"},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150
    )

    return chat_response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    school_id = "Ralph University" 
    user_input = "List all the student services"
    response = query_chatbot(school_id, user_input)
    print(f"Chatbot ({school_id}):", response)
