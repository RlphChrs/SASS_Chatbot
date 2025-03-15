from config import index, openai

# query chatbot for a specific school
def query_chatbot(school_id, user_input):
    # Convert user input to vector
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=user_input
    )
    query_vector = response.data[0].embedding

    # ensuring pincecon index is correctly formatted
    search_results = index.query(
        vector=query_vector,  # ✅ Must use keyword argument
        top_k=3,
        filter={"school": school_id},  # ✅ Filter by school
        include_metadata=True
    )

    # handling case where no results are found
    matches = search_results.get("matches", [])
    if not matches:
        return "I'm sorry, but I couldn't find any relevant information."

    # rxtract relevant text chunks
    retrieved_texts = "\n\n".join([match["metadata"]["text"] for match in matches])

    # Generate chatbot response using OpenAI
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
    user_input = "List the classroom procedure"
    response = query_chatbot(school_id, user_input)
    print(f"Chatbot ({school_id}):", response)
