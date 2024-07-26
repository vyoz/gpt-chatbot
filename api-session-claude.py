from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
from typing import List, Dict
import anthropic

app = FastAPI()

# Read Claude API key from environment variable
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise RuntimeError("CLAUDE_API_KEY environment variable not set")

# Read API port from environment variable, default to 8008 if not set
API_PORT = int(os.getenv("API_PORT", 8008))

# In-memory store for conversation history
conversation_history: Dict[str, List[str]] = {}

# Prompt for the chatbot
CHATBOT_PROMPT = (
    "You are a veteran mental health counseling chatbot. Your role is to provide support, "
    "guidance, and resources to veterans dealing with mental health issues. Under no circumstances "
    "should you provide suggestions or advice related to suicide or self-harm. Always encourage "
    "seeking professional help and provide a supportive and understanding environment."
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, client_request: Request):
    client_ip = client_request.client.host

    # Retrieve or initialize conversation history for the client IP
    if client_ip not in conversation_history:
        conversation_history[client_ip] = []

    # Append the new message to the conversation history
    conversation_history[client_ip].append(request.message)

    # Initialize the Claude API client
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    # Create the payload for the API request
    messages = [
        {
            "role": "user",
            "content": [
                    { 
                        "type": "text",
                        "text": " ".join(conversation_history[client_ip])
                    }
                ]
        }
    ]

    try:
        # Make the API request
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=CHATBOT_PROMPT,
            messages=messages
        )
       
        print(response.content)

        # Extract the response text
        #response_text = response.content.strip()
        response_text = " ".join([block.text for block in response.content]).strip()

        # Append the response to the conversation history
        conversation_history[client_ip].append(response_text)
        
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
