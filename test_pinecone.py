from config import index

def check_pinecone():
    print("🔹 Checking Pinecone Index...")
    print(index.describe_index_stats())  # Fetch Pinecone index stats

if __name__ == "__main__":
    check_pinecone()
