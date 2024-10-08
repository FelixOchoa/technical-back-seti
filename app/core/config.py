import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials
from firebase_admin import firestore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase Configs

credFB = credentials.Certificate("fund-db-5d5236e74db6.json")
app_fs = firebase_admin.initialize_app(credFB)
db_fs = firestore.client()
