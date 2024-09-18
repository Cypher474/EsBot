# ESBOT Backend
 ESBOT is a FastAPI-based backend for a chatbot designed to handle student inquiries. It offers multilingual
capabilities, session state management, and the ability to store and
retrieve previous chat history. It is tailored to help students with
academic-related questions, leveraging OpenAI\'s language model for
intelligent responses.

# Key Features Multilingual Capability:
 The bot can respond in multiple
languages, adjusting to the user\'s preferred language. Session
Management: Each chat session is maintained through session state,
ensuring smooth conversations across multiple interactions. Chat
History: The system stores previous conversations, allowing users to
retrieve their chat history at any time. How to Clone and Run the
Repository Clone the Repository First, clone the repository to your
local machine using:

bash Copy code git clone
https://github.com/yourusername/esbot-backend.git cd esbot-backend
# Install Dependencies Before running the project, make sure to install
all the required dependencies. You can do this by using:

# bash Copy code pip install -r requirements.txt Run the Application To
run the application using uvicorn, simply run:
# uvicorn main:app --host 0.0.0.0 --port 8000
bash Copy code uvicorn main:app \--reload This will start the FastAPI
application and serve it at http://127.0.0.1:8000.

Example Code Snippet Here is a quick overview of the backend structure
and key imports:

python Copy code from fastapi import FastAPI, HTTPException, APIRouter,
Depends from pydantic import BaseModel from fastapi.middleware.cors
import CORSMiddleware from starlette.middleware.sessions import
SessionMiddleware import mysql.connector import openai import os

\# Load environment variables and initialize FastAPI app app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=\"secret_signing_key\")
app.add_middleware(CORSMiddleware, allow_origins=\[\"\*\"\],
allow_methods=\[\"\*\"\], allow_headers=\[\"\*\"\]) Environment
Variables Make sure to set up your .env file with the following keys:

OPENAI_API_KEY: Your OpenAI API key. DB_CONFIG: Database connection
details for MySQL. ASSISTANT_ID: The assistant ID for OpenAI API
integration. API Endpoints Login Endpoint Allows users to log in with
email and password:

bash Copy code POST /login Chat Endpoint Submits user queries and
retrieves responses from the assistant:

bash Copy code POST /chat History Endpoint Fetches the chat history for
a given session:

bash Copy code POST /history/ Logout Endpoint Clears session data:

bash Copy code POST /logout License This project is licensed under the
MIT License.
