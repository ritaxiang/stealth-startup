import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agent import Agent

load_dotenv()

# Initialize the Slack WebClient with Bot User OAuth Token
slack_token = os.getenv("IAN_K_SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

# Webhook URL for sending responses
slack_webhook_url = os.getenv("IAN_K_SLACK_WEBHOOK")

# Initialize the agent
cohere_api_key = os.getenv("COHERE_API_KEY")
ceo_agent = Agent(name="Alice", role="CEO", cohere_api_key=cohere_api_key)

# Function to read messages from a specific Slack channel
def read_slack_messages(channel_id, limit=10):
    try:
        print("trace1")
        response = client.conversations_history(channel=channel_id, limit=limit)
        print("trace2")
        messages = response['messages']
        print("trace3")
        return messages
    except SlackApiError as e:
        print(f"Error retrieving messages: {e.response['error']}")
        return []

# Function to format and send a response to Slack using the webhook
def send_message_to_slack(message, webhook_url):
    headers = {'Content-Type': 'application/json'}
    data = {"text": message}
    response = requests.post(webhook_url, json=data, headers=headers)
    if response.status_code == 200:
        print("Message sent to Slack successfully.")
    else:
        print(f"Failed to send message to Slack: {response.status_code}, {response.text}")

# Process messages and respond based on the agent's logic
def process_messages_and_respond(channel_id):
    messages = read_slack_messages(channel_id)

    for msg in messages:
        user_message = msg['text']
        print(f"Received message: {user_message}")

        # Pass the message to the agent to generate a response
        ceo_agent.take_instruction(user_message)

        # Get agent's memory (the response)
        memory = ceo_agent.recall_memory()
        formatted_response = format_memory_for_slack(memory)

        # Send the agent's response back to Slack using the webhook
        send_message_to_slack(formatted_response, slack_webhook_url)

# Helper function to format the agent's memory for Slack
def format_memory_for_slack(memory):
    messages = []
    for entry in memory:
        instruction = entry['instruction']
        action = entry['action']
        messages.append(f"Instruction: {instruction}\nAction: {action}\n")
    return "\n".join(messages)

if __name__ == "__main__":
    channel_id = "C07N3SLH5EU" # social channel
    
    # Read messages from the channel and respond
    process_messages_and_respond(channel_id)
