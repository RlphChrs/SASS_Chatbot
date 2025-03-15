from fastapi import FastAPI
from store_pdfs import store_pdfs 
from query_chatbot import query_chatbot  
from pydantic import BaseModel

app = FastAPI()

# Define request model for chatbot API
class ChatRequest(BaseModel):
    school_id: str
    user_input: str

@app.post("/process_file")
def process_uploaded_file(data: dict):
    file_path = data["file_path"]

    # Extract school ID and filename from file path
    parts = file_path.split("/")
    school_id = parts[1]  # Example: "uc-banilad"
    file_name = parts[-1]  # Example: "enrollment_guide.pdf"

    print(f" Processing uploaded file for school: {school_id}")

    # Automatically process and store the file
    store_pdfs(school_id, file_name)

    return {"status": "success", "message": f"Processed {file_name} for {school_id}"}

# API Endpoint
@app.post("/chatbot")
def chatbot_response(request: ChatRequest):
    response_text = query_chatbot(request.school_id, request.user_input)
    return {"response": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
