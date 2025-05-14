import os
import openai
import pinecone
from pdfminer.high_level import extract_text
from config import bucket, index

TEMP_DIR = os.path.abspath("temp")

def extract_text_from_pdf(school_id, file_name):
    local_path = os.path.join(TEMP_DIR, f"{school_id}_{file_name}")
    os.makedirs(TEMP_DIR, exist_ok=True)

    # download file from Firebase Storage
    blob = bucket.blob(f"schools/{school_id}/pdfs/{file_name}")
    blob.download_to_filename(local_path)

    # extract text from PDF
    text = extract_text(local_path)
    return text

# chunk text into smaller parts
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Store extracted text in Pinecone
def store_pdfs(school_id, file_name):
    text = extract_text_from_pdf(school_id, file_name)
    text_chunks = chunk_text(text, chunk_size=500)

    for i, chunk in enumerate(text_chunks):
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=chunk
        )
        vector = response.data[0].embedding

        #Store in Pinecone with fileName for deletion later
        metadata = {
            "school": school_id,
            "source": file_name,  
            "text": chunk
        }

        index.upsert([(f"{school_id}_{file_name}_{i}", vector, metadata)])

        print(f" Stored chunk {i} for {school_id} ({file_name}) in Pinecone")
