import openai
import os

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize conversation history
conversation_history = []

print("Dr. Sanchez: Hello, I'm Dr. Sanchez, a therapist specializing in veteran mental health. How can I help you today?")

while True:
    # Get user input
    user_message = input("You: ")
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})
    
    # Generate response using GPT-4
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Dr. Sanchez, a compassionate therapist specializing in veteran mental health."},
            *conversation_history
        ]
    )
    
    # Extract and print AI response
    ai_message = response.choices[0].message['content']
    print(f"Dr. Sanchez: {ai_message}")
    
    # Add AI response to conversation history
    conversation_history.append({"role": "assistant", "content": ai_message})
    
    # Limit conversation history to last 10 messages
    conversation_history = conversation_history[-10:]
