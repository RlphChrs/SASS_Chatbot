from fastapi import FastAPI
from store_pdfs import store_pdfs  # Import function to process PDFs

app = FastAPI()

@app.post("/process_file")
def process_uploaded_file(data: dict):
    file_path = data["file_path"]

    # 🔹 Extract school ID and filename from file path
    parts = file_path.split("/")
    school_id = parts[1]  # Example: "uc-banilad"
    file_name = parts[-1]  # Example: "enrollment_guide.pdf"

    print(f"📂 Processing uploaded file for school: {school_id}")

    # 🔹 Automatically process and store the file
    store_pdfs(school_id, file_name)

    return {"status": "success", "message": f"Processed {file_name} for {school_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
