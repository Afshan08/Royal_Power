from flask import Flask, render_template, request, jsonify
import os
import json
import logging
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel
from agents import Runner
from agents.mcp import MCPServerStdio
import asyncio

app = Flask(__name__)

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/find-dealer')
def find_dealer():
    return render_template('find_dealer.html')

@app.route('/api/dealers')
def api_dealers():
    try:
        with open('dealers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([])



# --- Backend Chatbot Logic ---

# Configure OpenAI client for Gemini
# Note: Using the key provided by the user. In a real app, use environment variables.

external_client = AsyncOpenAI( 
    api_key="AIzaSyDxSISfrb-EM6W83ioGV4wn3cj5KL7BwQ4",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-3-flash-preview",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    system_prompt = """You are a helpful and knowledgeable AI assistant for 'Royal Power Motorcycles', a premium motorcycle showroom in Peshawar, Pakistan.
    
    Your goal is to assist customers with:
    1. Product Information: Provide details about Royal Power bikes (RP-70: PKR 125,000, RP-125: PKR 185,000, RP-150: PKR 240,000). Emphasize quality, fuel efficiency, and durability.
    2. Services: We offer servicing (starting PKR 2,000), genuine parts, and repairs.
    3. Location: Ring Road, Peshawar.
    4. Filing Complaints/Quotes: Guide users to the 'Contact Us' page for formal complaints, vendor quotes, or supplier inquiries.
    
    Tone: Professional, friendly, and 'Royal' (polite and respectful).
    Keep responses concise (under 3 sentences where possible) as this is a chat interface.
    """

    try:
        async def CustomerSupportAgent():
        # Define the agent with prompt
            agent = Agent(
                name="Customer Support Agent",
                instructions=system_prompt,
                model=model,
            )
                
            answer = await Runner.run(agent, user_message)
            print("Customer Support Agent answer:", answer.final_output)
            return answer.final_output
        
        bot_reply = asyncio.run(CustomerSupportAgent())
    except Exception as e:
        print(f"Error calling AI: {e}")
        bot_reply = "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again later."
        
    return jsonify({'response': bot_reply})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
