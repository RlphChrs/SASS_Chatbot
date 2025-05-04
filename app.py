from fastapi import FastAPI
from store_pdfs import store_pdfs 
from query_chatbot import query_chatbot  
from pydantic import BaseModel
import asyncio

app = FastAPI()

# Define request model for chatbot API
class ChatRequest(BaseModel):
    schoolId: str   
    studentId: str 
    userInput: str  


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


# ✅ Async chatbot endpoint using executor to avoid blocking
@app.post("/chatbot")
async def chatbot_response(request: ChatRequest):
    loop = asyncio.get_event_loop()
    response_text = await loop.run_in_executor(
        None, lambda: query_chatbot(request.schoolId, request.userInput)
    )
    return {"botResponse": response_text}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
