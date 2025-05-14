from config import index, openai

# In-memory cache for repeated questions
chat_cache = {}

# List of categories that MUST use document-based answers
pdf_categories = {
    "admission", "enrollment", "retention", "withdrawal", "transfer", "grading", "examinations",
    "attendance", "student services", "scholarship", "guidance", "medical", "academic conduct",
    "student organizations", "off-campus activity", "discipline", "fees", "registrar", "library",
    "shipboard training", "graduation", "honor graduates", "code of conduct", "academic programs"
}

# Query chatbot for a specific school
def query_chatbot(school_id, user_input):
    cache_key = f"{school_id}:{user_input}"
    if cache_key in chat_cache:
        return chat_cache[cache_key]

    # --- Step 1: Classify the query ---
    classification_prompt = [
        {
            "role": "system",
            "content": (
                "You are a classifier for a university chatbot. Categorise the student's query into one of the following:\n"
                "'admission', 'enrollment', 'retention', 'withdrawal', 'transfer', 'grading', 'examinations', 'attendance', "
                "'student services', 'scholarship', 'guidance', 'medical', 'academic conduct', 'student organizations', "
                "'off-campus activity', 'discipline', 'fees', 'registrar', 'library', 'shipboard training', "
                "'graduation', 'honor graduates', 'code of conduct', 'academic programs', 'emotional support', 'technical issue', "
                "'casual', 'other'.\n"
                "Only return the category name. Do not explain."
            )
        },
        {
            "role": "user",
            "content": f"Query: {user_input}\nCategory:"
        }
    ]

    try:
        classification_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=classification_prompt,
            max_tokens=10
        )
        category = classification_response.choices[0].message.content.strip().lower()
    except Exception as e:
        print("❌ Classification failed:", e)
        category = "other"

    print(f"🧠 Category identified: {category}")

    # --- Step 2: Handle document-based queries ---
    if category in pdf_categories:
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=user_input
            )
            query_vector = response.data[0].embedding

            search_results = index.query(
                vector=query_vector,
                top_k=8,
                filter={"school": school_id},
                include_metadata=True
            )

            matches = search_results.get("matches", [])

            if not matches:
                return "I'm sorry, but I couldn't find any relevant information in the school documents."

            retrieved_texts = "\n\n".join([
                match["metadata"]["text"]
                for match in matches
            ])

            print("📥 Retrieved Context for GPT:\n", retrieved_texts)
            print("❓ User Question:", user_input)

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

            chat_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=400
            )

            final_response = chat_response.choices[0].message.content
            chat_cache[cache_key] = final_response
            return final_response

        except Exception as e:
            print("❌ PDF search failed:", e)
            return "I'm sorry, I encountered an error while processing your request."

    # --- Step 3: Handle non-PDF queries via GPT conversational mode ---
    try:
        fallback_prompt = [
            {
                "role": "system",
                "content": (
                    f"You are a friendly and supportive student affairs chatbot for '{school_id}'. "
                    "If the student expresses emotions, frustration, or confusion, respond empathetically. "
                    "You may also engage in casual talk, encouragement, or friendly suggestions."
                )
            },
            {"role": "user", "content": user_input}
        ]

        chat_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=fallback_prompt,
            max_tokens=300
        )

        final_response = chat_response.choices[0].message.content
        chat_cache[cache_key] = final_response
        return final_response

    except Exception as e:
        print("❌ GPT fallback failed:", e)
        return "I'm sorry, I couldn't generate a response at the moment. Please try again later."
