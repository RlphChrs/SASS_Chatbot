import openai

# Function to test OpenAI connection with the new API
def test_openai():
    client = openai.OpenAI(api_key="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") 

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
    )
    print(response.choices[0].message.content)  # ✅ Corrected output format

if __name__ == "__main__":
    test_openai()
