# Capstone Project – Chatbot Backend

This is the **chatbot backend** for my capstone project, built using **Python** and **FastAPI**. It serves as the **brain behind student-facing responses**, enabling the chatbot to answer student queries based on school-uploaded documents.

The backend is triggered by the **SAO Admin backend** whenever a school uploads a PDF document. Upon receiving a trigger, it:

-  Extracts text from the PDF
-  Generates **vector embeddings** using a language model (e.g., OpenAI)
-  Stores the embeddings in **Pinecone** for efficient **semantic search**
-  Enables intelligent and context-aware responses based on school documents

---

##  Features

- 📄 PDF document parsing and preprocessing
- 🧠 Embedding generation using OpenAI 
- 📚 Vector storage and indexing in **Pinecone**
- 🔗 FastAPI-powered API endpoints
- 🏫 Multi-tenant architecture (isolates vectors per school)

---

## Tech Stack

| Component | Tech |
|----------|------|
| Backend Framework | FastAPI |
| Language | Python |
| PDF Parsing | 
| Embedding Model | OpenAI Embeddings |
| Vector Database | Pinecone |
| Environment Config | Python `dotenv` |

---

⚠️ Security Note
🔐 Important:
This repository previously contained a file that included all API credentials (e.g., OpenAI, Pinecone) as part of its history. However, these credentials have since been revoked and deleted, and the associated services are no longer accessible using those keys.

Always store secrets in a .env file and never commit sensitive credentials to version control. Use tools like .gitignore and secret scanning to prevent this in future projects.

---

## Author
Ralph Pilapil
Email: ralphc.pilapil@gmail.com
