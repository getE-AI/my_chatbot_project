# app.py

import os
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import requests

app = Flask(__name__)

# Configure server-side session
app.config['SECRET_KEY'] = 'freedom'  # You can replace 'freedom' with your desired secret key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Your API key and endpoint
API_KEY = os.environ.get('API_KEY')
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Load the system prompt from the environment variable
SYSTEM_PROMPT = os.environ.get('SYSTEM_PROMPT')

# Ensure that SYSTEM_PROMPT is set
if not SYSTEM_PROMPT:
    raise ValueError("SYSTEM_PROMPT environment variable not set.")

def get_bot_response(user_input):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Retrieve conversation history from the session
    messages = session.get('messages', [])

    # If messages are empty, start with the system prompt
    if not messages:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # Add the user's message to the conversation
    messages.append({"role": "user", "content": user_input})

    data = {
        "model": "anthropic/claude-3-haiku:beta",  # Correct model identifier
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raises HTTPError for bad responses
        result = response.json()
        assistant_message = result['choices'][0]['message']['content'].strip()

        # Add the assistant's response to the conversation
        messages.append({"role": "assistant", "content": assistant_message})

        # Save the updated messages back to the session
        session['messages'] = messages

        return assistant_message
    except requests.exceptions.HTTPError as e:
        # Print the error and response for debugging
        print(f"HTTP error occurred: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
        return "Sorry, I'm having trouble processing your request right now."
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I'm having trouble processing your request right now."

@app.route('/')
def home():
    # Clear the conversation history when the user accesses the home page
    session.clear()
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    bot_response = get_bot_response(user_input)
    return jsonify({'bot_response': bot_response})

if __name__ == '__main__':
    # Use the port specified by the environment or default to 5000
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
