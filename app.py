import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agent import CEO
from dictator import Dictator
import time

# Load environment variables from .env file
load_dotenv()

# Initialize the Slack WebClient with Bot User OAuth Token

# Initialize the agent
cohere_api_key = os.getenv("COHERE_API_KEY")
slack_token = os.getenv("IAN_K_SLACK_BOT_TOKEN")
ceo_slack_id = "U07M0K20NB1"
client = WebClient(token=slack_token)
#ceo_slack_id = os.getenv("CEO_SLACK_ID")  # The Slack ID for the CEO

# Initialize the CEO agent
ceo_agent = CEO(name="Alice", id=ceo_slack_id, cohere_api_key=cohere_api_key, slack_token=slack_token)

employees = {ceo_agent.id: ceo_agent}
#print(employees)
dictator = Dictator(name="Dictator", cohere_api_key=cohere_api_key, employees=employees, channel_id="C07M9C6G0LW")

# CEO executes a task (e.g., setting up company goals)
#ceo_agent.take_instruction("the AI-driven healthcare market")

channel_id = "C07M9C6G0LW"  # Replace with your actual Slack channel ID
messages = []

while True:
    time.sleep(5)
    try:
        response = client.conversations_history(channel=channel_id, limit=6)
        #print(response)
        messages = response['messages']
        if len(messages) > 0:
            dictator.process_message(messages)
    except SlackApiError as e:
        print(f"Error retrieving messages: {e.response['error']}")
        messages = []
