import os
import requests
from dotenv import load_dotenv 
from agent import Agent

load_dotenv()

# Initialize the agent with a name, role, and Cohere API key
cohere_api_key = os.getenv("COHERE_API_KEY")  # Load from env variable or set directly
slack_webhook_url = os.getenv("IAN_K_SLACK_WEBHOOK")
ceo_agent = Agent(name="Alice", role="CEO", cohere_api_key=cohere_api_key)

# CEO receives an instruction to brainstorm product ideas
ceo_agent.take_instruction("brainstorm product ideas for an AI-powered calendar app")

# Check memory for previous actions
memory = ceo_agent.recall_memory()
print("Memory:", memory)

# Function to format the agent's memory for Slack
def format_memory_for_slack(memory):
    # Convert the memory list into a formatted string for Slack
    messages = []
    for entry in memory:
        instruction = entry['instruction']
        action = entry['action']
        messages.append(f"Instruction: {instruction}\nAction: {action}\n")
    return "\n".join(messages)

# Function to send the message to Slack via the Webhook
def send_message_to_slack(message, webhook_url):
    headers = {'Content-Type': 'application/json'}
    data = {"text": message}
    response = requests.post(webhook_url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("Message sent to Slack successfully.")
    else:
        print(f"Failed to send message to Slack: {response.status_code}, {response.text}")

# Format the memory into a message for Slack
slack_message = format_memory_for_slack(memory)

# Send the formatted message to Slack
send_message_to_slack(slack_message, slack_webhook_url)
