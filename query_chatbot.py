from config import index, openai

# Optional in-memory cache for repeated questions
chat_cache = {}

# Query chatbot for a specific school
def query_chatbot(school_id, user_input):
    cache_key = f"{school_id}:{user_input}"
    if cache_key in chat_cache:
        return chat_cache[cache_key]

    # Convert user input to vector
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=user_input
    )
    query_vector = response.data[0].embedding

    # Query Pinecone with a broader context window
    search_results = index.query(
        vector=query_vector,
        top_k=10,  # Increased to improve retrieval accuracy
        filter={"school": school_id},
        include_metadata=True
    )

    matches = search_results.get("matches", [])
    if not matches:
        return "I'm sorry, but I couldn't find any relevant information in the school documents."

    # Extract full text chunks
    retrieved_texts = "\n\n".join([
        match["metadata"]["text"]
        for match in matches
    ])

    # 🔍 Log retrieved content for debugging
    print("📥 Retrieved Context for GPT:\n", retrieved_texts)
    print("❓ User Question:", user_input)

    # Strict system prompt to prevent hallucination
    system_prompt = (
        f"You are a helpful and factual school assistant for '{school_id}'.\n"
        "ONLY use the following context to answer the user's question.\n"
        "If the answer is not found in the context, clearly respond with:\n"
        "'I'm sorry, I couldn't find that information in the documents.'\n\n"
        "DO NOT guess or make up your own answer.\n"
        "DO NOT rely on outside knowledge.\n"
        "DO NOT include details not mentioned in the context.\n\n"
        f"Context:\n{retrieved_texts}"
    )

    # Generate chatbot response using GPT-4
    chat_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=500
    )

    final_response = chat_response.choices[0].message.content
    chat_cache[cache_key] = final_response

    return final_response
