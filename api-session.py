from flask import Flask, request, jsonify, session
from flask_session import Session
import openai
import os

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    ip_address = request.remote_addr

    if 'conversation_history' not in session:
        session['conversation_history'] = []

    conversation_history = session['conversation_history']
    conversation_history.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Dr. Sanchez, a compassionate therapist specializing in veteran mental health."},
            *conversation_history
        ]
    )

    ai_message = response.choices[0].message['content']
    conversation_history.append({"role": "assistant", "content": ai_message})
    
    session['conversation_history'] = conversation_history[-10:]

    # Print session history for debugging
    print(f"Session History for IP {ip_address}:")
    for message in session['conversation_history']:
        print(f"{message['role']}: {message['content']}")
    print("------------------------")


    return jsonify({"response": ai_message})

if __name__ == '__main__':
    app.run(debug=True)
