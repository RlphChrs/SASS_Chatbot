import firebase_admin
from firebase_admin import credentials, storage
from pinecone import pinecone, ServerlessSpec
import openai

#  Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json") 
firebase_admin.initialize_app(cred, {"storageBucket": "sass-db-946b7.firebasestorage.app"})
bucket = storage.bucket()

#  Initialize Pinecone
PINECONE_API_KEY = "pcsk_61pDm4_TgPbNSptfs3ppJ9q966sRUenSgX3zZ9bwUNaNH3LjH4wniboTe8MxQdWHPfWuDm"
PINECONE_ENVIRONMENT = "us-east-1"

pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pinecone_client.Index("chatbot") 

#  OpenAI API Key
openai.api_key = "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"
