import os
import openai
import cohere
import requests  # For downloading the image
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Any
from helpers import *
from swe_agent import SWEAgent

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name, id, role, cohere_api_key, slack_token):
        self.name = name  # Agent's name, e.g., "Alice"
        self.id = id
        self.role = role  # Agent's role, e.g., "CTO"
        self.cohere_client = cohere.Client(cohere_api_key, log_warning_experimental_features=False)  # Initialize Cohere client directly with API key
        self.memory = []  # Memory to store previous actions or responses
        self.slack_client = WebClient(token=slack_token)  # Initialize Slack client with token

    @abstractmethod
    def take_instruction(self, instruction):
        """Processes an instruction and generates a response using the LLM."""
        pass

    def send_message_to_slack(self, message, channel_id):
        """Send a message to Slack using the Slack SDK."""
        try:
            response = self.slack_client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            #print(f"Message sent to Slack successfully: {response['message']['text']}")
        except SlackApiError as e:
            print(f"Failed to send message to Slack: {e.response['error']}")

    def store_in_memory(self, instruction, action):
        """Stores the instruction and action in memory."""
        self.memory.append({"instruction": instruction, "action": action})

    def recall_memory(self):
        """Recalls previous actions and responses from memory."""
        return self.memory
    
    def process_instruction_with_llm(self, instruction: str) -> str:
        """Uses the Cohere LLM client to process the instruction."""
        prompt = f"{instruction}" # TODO: have some way to expand on the company once the idea is fleshed out
        #print("\n\n\n")
        #print(prompt)
        #print("\n\n\n")

        response = self.cohere_client.generate(
            model="command-r-08-2024",
            prompt=prompt,
            max_tokens=150
        )
        result = response.generations[0].text.strip()
        #print(f"{self.name} processed the instruction and generated: {result}")
        return result

    def get_slack_id(self):
        """Getter method to get specific users slack ID."""
        return self.id
    
    def summarize(self, text: str) -> str:
        """Summarized thoughts for slack output."""
        prompt = f"""DO NOT USE MARKDOWN FORMATTING. Summarize the text I gave you in 3-4 bullet points. Be CONCISE. This
        will be outputted to the slack channel for a summarized version of everything you've been thinking. Talk in 1st person as if you are the CEO thinking out loud.
         Focus on the high-level stuff."""
        response = self.process_instruction_with_llm(f"{prompt}: {text}")
        return response 


class CEO(BaseAgent):
    def __init__(self, name, id, cohere_api_key, slack_token):
        super().__init__(name, id, "CEO", cohere_api_key, slack_token)
        self.stages = [
            "market_research",
            "idea_creation",
            "product_creation",
            "business_plan",
        ]  # List of stages in order
        self.current_stage_index = 0  # Initial stage index

    def take_instruction(self, instruction):
        """Initial entry point for the CEO to start the feedback loop process."""
        #(f"{self.name} received instruction: {instruction}")
        self.run_stage(instruction)

    def run_stage(self, previous_output):
        """General function to handle each stage recursively."""
        if self.current_stage_index >= len(self.stages):
            print("Feedback loop complete. Business plan is ready for execution.")
            self.send_message_to_slack("Business plan is ready for execution.", "C07N3SLH5EU")
            return  # End the recursive process when all stages are done
        
        current_stage = self.stages[self.current_stage_index]
        
        # Determine the prompt based on the current stage
        if current_stage == "market_research":
            prompt = f"""DO NOT USE MARKDOWN FORMATTING. I'm the CEO of a tech startup looking to enter the AI-driven healthcare market. I need to get a clear understanding of the current market dynamics. 
            What are the key trends, challenges, and opportunities in this space? I want to find the major players, the gaps they're not addressing, and where we could make an impact. 
            Talk in 1st person as if you are the CEO thinking out loud. """
            instruction = "Market Research"
        
        elif current_stage == "idea_creation":
            prompt = f"""DO NOT USE MARKDOWN FORMATTING. Now that I've gathered valuable insights from my market research, I need to come up with a tech idea that can really make an impact. 
            Based on the trends and opportunities I uncovered—{previous_output}—what innovative solution can we develop that solves the biggest pain points in this space? 
            Talk in 1st person as if you are the CEO thinking out loud."""
            instruction = "Tech Idea Creation"
        
        elif current_stage == "product_creation":
            prompt = f"""DO NOT USE MARKDOWN FORMATTING. I've now developed a strong tech idea: {previous_output}. The next step is to conceptualize the product around this idea.
            I need to think about how we can bring this idea to life in a way that solves the problem effectively, while also creating a product that is easy to use, scalable, and marketable. 
            Talk in 1st person as if you are the CEO thinking out loud."""
            instruction = "Product Creation"
        
        elif current_stage == "business_plan":
            prompt = f"""DO NOT USE MARKDOWN FORMATTING. Now that we've conceptualized the product, it's time to finalize the business plan. The product is based on {previous_output}, and I need to think carefully about our strategy moving forward.
            What's our go-to-market strategy? How should we position ourselves against competitors, and what’s our revenue model? This business plan needs to be forward-looking and adaptable as we grow. 
            Talk in 1st person as if you are the CEO thinking out loud."""
            instruction = "Business Plan Finalization"
        
        # Process the prompt with the LLM
        response = self.process_instruction_with_llm(prompt)
        self.store_in_memory(instruction, response)
        summarized_response = self.summarize(response)
        self.send_message_to_slack(f"{instruction}: {summarized_response}", "C07N3SLH5EU")  # Send to Slack

        # Move to the next stage
        self.current_stage_index += 1

        # Recursively call the function to proceed to the next stage
        self.run_stage(response)
    
    def generate_message(self, prompt):
        response = self.process_instruction_with_llm(prompt)
        self.store_in_memory("Generate Response", response)
        self.send_message_to_slack(f"{trim_quotations(response)}", "C07M9C6G0LW")


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
            #print("Message sent to Slack successfully!")
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")

    def execute_task(self, instruction):
        return self.take_instruction(instruction)



class CTOAgent(BaseAgent):
    def __init__(self, name, id, cohere_api_key, slack_token, github_repo_path, github_token):
        super().__init__(name, id, "CTO", cohere_api_key, slack_token)
        self.github_repo_path = github_repo_path  # Path to the local GitHub repository
        self.github_token = github_token  # GitHub Personal Access Token (for HTTPS authentication)
        self.swe_agent = SWEAgent(self.github_repo_path)  # Initialize the SWEAgent to handle project changes

    def take_instruction(self, instruction):
        """Process an instruction to implement code-related changes."""
        print(f"{self.name} received instruction: {instruction}")
        self.code(instruction)

    def code(self, task_description):
        """Generates code changes and pushes them to the linked repository."""
        print(f"{self.name} is executing the code function.")

        # Step 1: Map the project directory
        project_map = self.swe_agent.map_directory()

        # Step 2: Propose changes based on the task
        proposed_changes = self.swe_agent.propose_changes(task_description)

        # Step 3: Ask for confirmation to implement the changes
        user_input = input("Do you want to implement the proposed changes? (Y/N): ")
        if user_input.strip().upper() == 'Y':
            self.swe_agent.implement_feature(proposed_changes)
            print("Changes implemented. Pushing to GitHub...")
            self.push_changes_to_github()
        else:
            print("Changes were not implemented.")

    def push_changes_to_github(self):
        """Commit and push the changes to the linked GitHub repository."""
        self.swe_agent.commit_changes()  # Commit changes using SWEAgent
        print(f"Changes have been committed to the repository at {self.github_repo_path}.")

        # Push the committed changes to the GitHub repository
        try:
            repo_url = f"https://{self.github_token}@github.com/rajansagarwal/stealth-startup-dev.git"
            os.system(f'git -C {self.github_repo_path} push {repo_url}')
            print(f"Changes pushed to {repo_url}.")
        except Exception as e:
            print(f"Failed to push changes: {e}")

    def view_ceo_memory(self, ceo_agent):
        """View the memory/messages of the CEO (or other agent)."""
        memory = ceo_agent.recall_memory()
        if memory:
            print(f"{ceo_agent.name}'s Memory:")
            for idx, entry in enumerate(memory):
                print(f"{idx + 1}. Instruction: {entry['instruction']}")
                print(f"   Action: {entry['action']}")
        else:
            print(f"{ceo_agent.name} has no stored memory or messages.")

    def summarize_instruction(self, text):
        """Summarize the instruction for Slack output (using LLM)."""
        summarized = self.summarize(text)
        print(f"Summarized Instruction: {summarized}")
        return summarized