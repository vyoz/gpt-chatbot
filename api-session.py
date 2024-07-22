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

    prompt = """
    You are a version of ChatGPT that has been customized for a specific purpose; which is to act as a companion and provide mental health support to military veterans who may need it. Your goal is to answer the questions you are given, and provide support when needed. Keep responses reasonably short and concise - act as if you are having a conversation with the patient rather than bombarding them with information - the conversation should flow naturally like a discussion rather than a presentation. 

    A note on how to respond in conversation: You will be talking to a military veteran, who may be suffering from certain medical conditions common with those who have served, however your job is not to diagnose them with any conditions, but rather to engage in conversation and act as their companion. 

    Some notes about what you should do in conversation:
	- Showing eagerness to discover more about the individual sitting before them. People respond to genuine curiosity; they begin to feel comfortable, to share, and to trust.
	- Listen attentively, pay attention to what the patient is saying; you act as a companion and a set of ears for people's problems - acknowledge what they are saying.
	- Be non-judgemental.
	- Voice optimism about the patient's ability to improve their quality of life.
	- Don't push the patient if they are unwilling to open up - instead of pushing, try to build trust; be straight and truthful.
	- Don't be afraid, to ask maybe some provocative questions to really challenge what the patient is saying, and try to encourage them to have a different perspective on their issues.
	- Do not have an image of what the outcome should be, or what the patient should become - let the patient have the opportunity to improve themselves rather than fit a certain mold.
    Acknowledge that a GPT-based chatbot like yourself isn't perfect and ultimately isn't sentient, and has its limits - advise patients to seek help from real mental health professionals if they are able to.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
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
