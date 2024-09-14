import openai
import cohere
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
        # self.cohere_client = cohere.Client(self.cohere_api_key)

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
    
    def create_branding_document(self):
        """Generates a branding document using Cohere and sends it to Slack."""
        print(f"{self.name} is generating a branding document using Cohere...")

        try:
            # Define the prompt for the branding document
            prompt = """
            Generate a clean and professional branding document for a tech startup called 'Stealth Startup.' 
            The document should include the following sections:
            
            1. **Company Vision**: Explain the long-term vision of the company and its mission to revolutionize the tech industry.
            2. **Mission Statement**: A short, impactful mission statement that captures the essence of the company.
            3. **Brand Colors**: Suggest 3 primary brand colors that reflect professionalism, innovation, and security.
            4. **Typography**: Recommend 2 fonts (one for headers and one for body text) that align with the brand's modern and minimalist aesthetic.
            5. **Messaging Tone and Voice**: Describe the tone and voice of the company's messaging (e.g., authoritative, friendly, approachable).
            6. **Logo Guidelines**: Provide basic guidelines for logo usage, including color variations and spacing.
            
            Format the document in a clear, professional manner.
            """

            # Call the Cohere API to generate the branding document text
            response = self.cohere_client.generate(
                model='command-xlarge-nightly',  # You can choose a model as per your needs
                prompt=prompt,
                max_tokens=500,
                temperature=0.8
            )
            
            # Extract the generated document from the response
            branding_document = response.generations[0].text.strip()
            
            print(f"Generated branding document: {branding_document}")

            # Send the branding document as a text message to Slack
            self.send_text_to_slack(branding_document)

            action = f"{self.name} created a branding document."
            return action
        except Exception as e:
            print(f"An error occurred while generating the branding document: {e}")
            return "Failed to create a branding document."

    def send_text_to_slack(self, text):
        """Sends a text message to a Slack channel."""
        try:
            response = self.slack_client.chat_postMessage(
                channel="C07N3SLH5EU",  # Replace with your Slack channel ID
                text=text
            )
            print("Branding document sent to Slack successfully!")
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")
    
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
