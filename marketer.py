import openai
import requests  # For downloading the image
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agent import BaseAgent

class Marketer(BaseAgent):
    def __init__(self, name, id, role, cohere_api_key, slack_token, openai_api_key):
        super().__init__(name, id, role, cohere_api_key, slack_token)
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
        self.slack_client = WebClient(token=slack_token)

    def take_instruction(self, instruction):
        """Processes the instruction for branding, logo creation, or design work."""
        response = self.process_instruction_with_llm(instruction)

        if "logo" in instruction.lower():
            action = self.create_logo(instruction)
        elif "branding" in instruction.lower():
            action = self.create_branding_document()
        else:
            action = f"{self.name} processed the instruction: {response}"

        self.store_in_memory(instruction, action)
        return action
    
    def create_logo(self, prompt):
        """Generates a logo using OpenAI's DALL·E."""
        print(f"{self.name} is generating a logo with DALL·E...")

        try:
            # Call the OpenAI API to generate an image
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response["data"][0]["url"]
            print(f"Generated logo: {image_url}")

            # Send the logo URL to Slack instead of uploading the file
            self.send_image_link_to_slack(image_url, prompt)

            action = f"{self.name} created a new logo: {image_url}"
            return action
        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return "Failed to create a logo."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Failed to create a logo."

    def send_image_link_to_slack(self, image_url, prompt):
        """Sends the generated image link along with a message to a Slack channel."""
        try:
            response = self.slack_client.chat_postMessage(
                channel="C07N3SLH5EU",  # Replace with your Slack channel ID or name
                text=f"Here is the logo generated from the prompt: {prompt}\n{image_url}"
            )
            print("Message sent to Slack successfully!")
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")

    def execute_task(self, instruction):
        return self.take_instruction(instruction)
