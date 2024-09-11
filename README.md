# FastAPI Assistant Integration

## Overview

This project is a FastAPI-based web application that integrates with OpenAI's API to handle assistant interactions. The application includes endpoints to fetch and post message history and to interact with the assistant for processing user messages.

## Features

- **Fetch Message History**: Retrieve the history of messages between the user and the assistant.
- **Post Message History**: Post a new message and get the assistant's response.
- **Chat with Assistant**: Send a user message to the assistant and receive a response.

## Requirements

- Python 3.8+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [OpenAI](https://beta.openai.com/)
- [Python-dotenv](https://pypi.org/project/python-dotenv/)
- [Uvicorn](https://www.uvicorn.org/)

You can install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
