from fastapi import FastAPI, HTTPException
from store_pdfs import store_pdfs 
from query_chatbot import query_chatbot  
from pydantic import BaseModel
import asyncio
from config import index, pinecone_client 



app = FastAPI()

# Define request model for chatbot API
class ChatRequest(BaseModel):
    schoolId: str   
    studentId: str 
    userInput: str  


class DeleteChunksRequest(BaseModel):
    schoolId: str
    fileName: str


@app.post("/process_file")
def process_uploaded_file(data: dict):
    file_path = data["file_path"]

    # Extract school ID and filename from file path
    parts = file_path.split("/")
    school_id = parts[1]  
    file_name = parts[-1]  

    print(f" Processing uploaded file for school: {school_id}")

    # Automatically process and store the file
    store_pdfs(school_id, file_name)

    return {"status": "success", "message": f"Processed {file_name} for {school_id}"}


# chatbot endpoint using executor to avoid blocking
@app.post("/chatbot")
async def chatbot_response(request: ChatRequest):
    loop = asyncio.get_event_loop()
    response_text = await loop.run_in_executor(
        None, lambda: query_chatbot(request.schoolId, request.userInput)
    )
    return {"botResponse": response_text}


@app.post("/delete-chunks")
def delete_chunks(data: DeleteChunksRequest):
    try:
        print(f"🧹 Deleting chunks for file: {data.fileName} from school: {data.schoolId}")
        
        # Assume max 1000 chunks per file for safety
        prefix = f"{data.schoolId}_{data.fileName}_"
        ids_to_delete = [f"{prefix}{i}" for i in range(1000)]

        # Delete all 1000 potential chunks and Pinecone will ignore non-existent ones
        index.delete(ids=ids_to_delete)
        
        print("✅ Pinecone deletion completed using ID-based deletion.")
        return {"message": "Chunks deleted from Pinecone successfully"}

    except Exception as e:
        print("❌ Pinecone deletion failed:", str(e))
        raise HTTPException(status_code=500, detail="Failed to delete chunks from Pinecone")






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
