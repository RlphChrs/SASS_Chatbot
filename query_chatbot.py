from config import index, openai

# List of categories that MUST use document-based answers
pdf_categories = {
    "admission", "enrollment", "retention", "withdrawal", "transfer", "grading", "examinations",
    "attendance", "student services", "scholarship", "guidance", "medical", "academic conduct",
    "student organizations", "off-campus activity", "discipline", "fees", "registrar", "library",
    "shipboard training", "graduation", "honor graduates", "code of conduct", "academic programs", "student concerns", "disciplinary hearing",
    "misconduct", "complaints", "student reports", "student cases", "reporting issues", "violations",
    "lost and found", "id violations", "equipment borrowing", "replacement", "confiscated id"
}


# Query chatbot for a specific school
def query_chatbot(school_id, user_input, chat_history=None):
    vague_prompts = {"how much", "how much?", "amount", "fee", "price", "cost"}
    original_input = user_input.strip()
    rephrased_lower = original_input.lower()

    if original_input.lower() in vague_prompts and chat_history:
        last_topic = next((msg["content"] for msg in reversed(chat_history) if msg["role"] == "user"), None)
        if last_topic:
            user_input = f"{original_input} for {last_topic}"
            print(f"🪄 Rephrased user_input for context: {user_input}")
            rephrased_lower = user_input.lower()

    classification_prompt = [
        {
            "role": "system",
            "content": (
                "You are a classifier for a university chatbot. Categorise the student's query into one of the following topics:\n"
                "'admission', 'enrollment', 'retention', 'withdrawal', 'transfer', 'grading', 'examinations', 'attendance', "
                "'student services', 'scholarship', 'guidance', 'medical', 'academic conduct', 'student organizations', "
                "'off-campus activity', 'discipline', 'fees', 'registrar', 'library', 'shipboard training', "
                "'graduation', 'honor graduates', 'code of conduct', 'academic programs', "
                "'student concerns', 'lost and found', 'harassment', 'bullying', 'complaints', "
                "'emotional support', 'technical issue', 'casual', 'other'.\n\n"
                "Examples:\n"
                "- 'how much is uniform exemption' → fees\n"
                "- 'someone vaping' → violations\n"
                "- 'someone said im stupid' → bullying\n"
                "- 'hi' → casual\n"
                "Only return the category name."
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

    print(f"🧾 Rephrased: {rephrased_lower}")
    print(f"🧠 Category: {category}")

    # 🚨 Redirect sensitive concerns to guidance
    if category in {"bullying", "harassment"}:
        return (
            "I'm really sorry you're experiencing this. While I can't verify the situation, "
            "I strongly encourage you to speak with the Guidance Office so they can provide you with proper support and assistance. "
            "Your well-being matters."
        )

    # 📄 Search Pinecone for matches (if in allowed categories)
    if category in pdf_categories:
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=user_input
            )
            query_vector = response.data[0].embedding

            search_results = index.query(
                vector=query_vector,
                top_k=20,
                filter={"school": school_id},
                include_metadata=True
            )

            matches = search_results.get("matches", [])
            if not matches:
                return "I'm sorry, but I couldn't find any relevant information in the school documents."

            retrieved_texts = "\n\n".join([match["metadata"]["text"] for match in matches])

            system_prompt = (
                f"You are a helpful and factual student affairs assistant for '{school_id}'.\n"
                "Answer the student's question using ONLY the context provided below.\n"
                "If the question involves a violation (e.g. smoking, not wearing ID), kindly inform the student what type of violation it is (like Campus Conduct Violation or ID Violation), and advise them to report it to the SAO or appropriate office.\n"
                "Avoid claiming that you will report or notify anyone. Instead, suggest that the student inform the SAO.\n"
                "If the question is about processes, steps, or payment, answer clearly with what's found in the context.\n"
                "If no relevant answer is found, say: 'I'm sorry, I couldn't find that information in the documents.'\n"
                "Avoid saying 'the context states'. Respond naturally and politely.\n"
                f"\nContext:\n{retrieved_texts}"
            )

            messages = [{"role": "system", "content": system_prompt}]
            if chat_history:
                messages.extend(chat_history)
            messages.append({"role": "user", "content": user_input})

            chat_response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=400
            )

            return chat_response.choices[0].message.content

        except Exception as e:
            print("❌ PDF search failed:", e)
            return "I'm sorry, I encountered an error while processing your request."

    # 💬 Fallback GPT response if no PDF context available
    try:
        fallback_prompt = [
            {
                "role": "system",
                "content": (
                    f"You are a friendly and supportive student affairs chatbot for '{school_id}'.\n"
                    "Respond empathetically and helpfully."
                )
            }
        ]
        if chat_history:
            fallback_prompt.extend(chat_history)
        fallback_prompt.append({"role": "user", "content": user_input})

        chat_response = openai.chat.completions.create(
            model="gpt-4",
            messages=fallback_prompt,
            max_tokens=300
        )

        return chat_response.choices[0].message.content

    except Exception as e:
        print("❌ GPT fallback failed:", e)
        return "I'm sorry, I couldn't generate a response at the moment. Please try again later."
