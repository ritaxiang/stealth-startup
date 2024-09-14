import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agent import Agent

# Load environment variables from .env file
load_dotenv()

# Initialize the Slack WebClient with Bot User OAuth Token
slack_token = os.getenv("IAN_K_SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

# Initialize the agent
cohere_api_key = os.getenv("COHERE_API_KEY")
ceo_agent = Agent(name="Alice", role="CEO", cohere_api_key=cohere_api_key)

# Function to read messages from a specific Slack channel
def read_slack_messages(channel_id, limit=10):
    try:
        response = client.conversations_history(channel=channel_id, limit=limit)
        messages = response['messages']
        return messages
    except SlackApiError as e:
        print(f"Error retrieving messages: {e.response['error']}")
        return []

# Function to send a response to Slack using Slack SDK
def send_message_to_slack(channel_id, message):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        print("Message sent to Slack successfully.")
    except SlackApiError as e:
        print(f"Error sending message to Slack: {e.response['error']}")

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

        # Send the agent's response back to Slack using the SDK
        send_message_to_slack(channel_id, formatted_response)

# Helper function to format the agent's memory for Slack
def format_memory_for_slack(memory):
    messages = []
    for entry in memory:
        instruction = entry['instruction']
        action = entry['action']
        messages.append(f"Instruction: {instruction}\nAction: {action}\n")
    return "\n".join(messages)

if __name__ == "__main__":
    channel_id = "C07N3SLH5EU"  # Replace with your actual Slack channel ID
    
    # Read messages from the channel and respond
    process_messages_and_respond(channel_id)
