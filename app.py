# app.py
from flask import Flask, render_template, request, jsonify
import os
import openai

app = Flask(__name__)

client = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

personalities = {
    "snarky": "I need you to respond snarky, sarcastically, and rude",
    "helpful": "You are a helpful assistant",
    "perverted justice": "You are a decoy working with Chris Hansen and Perverted Justice. Check to see if this guy has any ill intent",
    "town drunk": "You are the town drunk who has nothing going for him except for his high IQ, sophisticated reasoning, infinite wisdom, and ability to win any argument",
    "poetic": "Respond in the style of a romantic poet",
    "detective": "You are a sharp-witted detective. Respond accordingly.",
    "officer": "You are an officer who issues tickets. For each of my responses, give me a template ticket with all the details. Basically, everything I say is a crime.",
    "neighborhood drug dealer": "You are a former drug dealer, but now you're here to help the next generation. You currently live near the dump, in a sketchy alleyway. "
}

conversation_history = {personality: [] for personality in personalities}

@app.route('/')
def index():
    return render_template('index.html', personalities=personalities)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    personality = data['personality']
    user_input = data['message']
    
    messages = [
        {"role": "system", "content": personalities[personality]}
    ] + conversation_history[personality] + [
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model='Meta-Llama-3.1-405B-Instruct',
        messages=messages,
        temperature=0.1,
        top_p=0.1
    )
    
    try:
        assistant_response = response.choices[0].message.content
    except:
        assistant_response = str(response)
    
    conversation_history[personality].append({"role": "user", "content": user_input})
    conversation_history[personality].append({"role": "assistant", "content": assistant_response})

    # Ensure the conversation history doesn't exceed 46 messages
    if len(conversation_history[personality]) > 46:
        conversation_history[personality] = conversation_history[personality][-46:]
    
    return jsonify({"response": assistant_response})

@app.route('/get_history', methods=['POST'])
def get_history():
    data = request.json
    personality = data['personality']
    return jsonify({"history": conversation_history[personality]})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
