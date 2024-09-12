# FastAPI OpenAI Integration

This project is a FastAPI application that integrates with the OpenAI API to allow users to interact with an assistant through streaming responses. It also includes endpoints for managing conversation history.

## Features

- **Streaming Responses:** Sends the assistant's responses to the client in a streaming format.
- **Conversation History:** Allows retrieval of past conversations with the assistant.
- **CORS Support:** Fully supports CORS to allow access from different origins.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/fastapi-openai-assistant.git
   cd fastapi-openai-assistant
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Create a .env file in the root directory with the following:

env
Copy code
OPENAI_API_KEY=your_openai_api_key
ASSISTANT_ID=your_assistant_id
THREAD_ID=your_thread_id
Run the application:

bash
Copy code
uvicorn main:app --reload
The application will be available at http://127.0.0.1:8000.

2. Endpoints
POST /retrieve100: Streams a response based on the user's query.
GET /history: Fetches the conversation history from the assistant.
POST /chat: Posts a message to the assistant and streams the response back.
Environment Variables
Ensure the following environment variables are set:
3. 
OPENAI_API_KEY: Your OpenAI API key.
ASSISTANT_ID: The ID of the assistant you are interacting with.
THREAD_ID: The thread ID to maintain conversation context.