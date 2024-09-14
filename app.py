import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agent import CEO

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

# CEO executes a task (e.g., setting up company goals)
ceo_agent.take_instruction("the AI-driven healthcare market")

ceo_agent.take_instruction("entering the AI-driven healthcare market")

# # Function to read messages from a specific Slack channel
# def read_slack_messages(channel_id, limit=10):
#     try:
#         response = client.conversations_history(channel=channel_id, limit=limit)
#         messages = response['messages']
#         return messages
#     except SlackApiError as e:
#         print(f"Error retrieving messages: {e.response['error']}")
#         return []

# # Function to send a response to Slack using Slack SDK
# def send_message_to_slack(channel_id, message):
#     try:
#         response = client.chat_postMessage(
#             channel=channel_id,
#             text=message
#         )
#         print("Message sent to Slack successfully.")
#     except SlackApiError as e:
#         print(f"Error sending message to Slack: {e.response['error']}")

# # Process messages and respond based on the agent's logic
# def process_messages_and_respond(channel_id):
#     messages = read_slack_messages(channel_id)

#     for msg in messages:
#         user_message = msg['text']
#         print(f"Received message: {user_message}")

#         # Pass the message to the agent to generate a response
#         ceo_agent.take_instruction(user_message)

#         # Get agent's memory (the response)
#         memory = ceo_agent.recall_memory()
#         formatted_response = format_memory_for_slack(memory)

#         # Send the agent's response back to Slack using the SDK
#         send_message_to_slack(channel_id, formatted_response)

# # Helper function to format the agent's memory for Slack
# def format_memory_for_slack(memory):
#     messages = []
#     for entry in memory:
#         instruction = entry['instruction']
#         action = entry['action']
#         messages.append(f"Instruction: {instruction}\nAction: {action}\n")
#     return "\n".join(messages)

# if __name__ == "__main__":
#     channel_id = "C07N3SLH5EU"  # Replace with your actual Slack channel ID
    
#     # Read messages from the channel and respond
#     process_messages_and_respond(channel_id)

# Marketer Testing
# import os
# import openai
# from dotenv import load_dotenv
# from agent import Marketer  # Import the Marketer class

# # Load environment variables from .env
# load_dotenv()

# # Initialize API keys and tokens
# slack_token = os.getenv("MARKET_TOKEN")
# cohere_api_key = os.getenv("COHERE_API_KEY")
# openai_api_key = os.getenv("OPENAI_API_KEY")

# # Initialize the marketer agent
# marketer = Marketer(
#     name="MarketingAgent",
#     id="U07M0K20NB1",  # Replace with the Slack ID of the agent
#     role="Marketing Specialist",
#     cohere_api_key=cohere_api_key,
#     slack_token=slack_token,
#     openai_api_key=openai_api_key
# )

# Example task to create a logo and send it to Slack
# instruction = "Create a minimalist pixel logo for a tech company"
# instruction = """
# Generate a modern, minimalist logo for a tech startup called 'Stealth Startup.' 
# The logo should reflect innovation, agility, and security. 
# Key elements to include:
# 1. **Monogram Design**: Create a sleek, professional monogram using the initials 'SS'. The design should be simple and modern, with clean lines.
# 2. **Color Scheme**: Use a dark or muted color palette with accent colors (such as dark blue, grey, or black) to convey professionalism and technological sophistication.
# 3. **Typography**: Include a sans-serif font that is clean, bold, and easy to read. The typography should complement the monogram and symbol without being overpowering.
# 4. **Style**: The overall design should be minimalist and futuristic, conveying a sense of trust and cutting-edge technology.

# Make the logo versatile so that it can be used for digital applications (websites, apps) and printed materials.
# """
# logo_response = marketer.execute_task(instruction)
# print(logo_response)

# Example task to create a branding document and send it to Slack
# instruction = "Create a branding document for a tech startup, be detailed please'"
# branding_response = marketer.create_branding_document()
# print(branding_response)
