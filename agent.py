import os
import cohere
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Any

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name, id, role, cohere_api_key, slack_token):
        self.name = name  # Agent's name, e.g., "Alice"
        self.id = id
        self.role = role  # Agent's role, e.g., "CTO"
        self.cohere_client = cohere.Client(cohere_api_key)  # Initialize Cohere client directly with API key
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
            print(f"Message sent to Slack successfully: {response['message']['text']}")
        except SlackApiError as e:
            print(f"Failed to send message to Slack: {e.response['error']}")

    def store_in_memory(self, instruction, action):
        """Stores the instruction and action in memory."""
        self.memory.append({"instruction": instruction, "action": action})

    # TODO: might not need
    def recall_memory(self):
        """Recalls previous actions and responses from memory."""
        return self.memory
    
    def process_instruction_with_llm(self, instruction):
        """Uses the Cohere LLM client to process the instruction."""
        prompt = f"As the {self.role} of a tech startup company, {instruction}" # TODO: have some way to expand on the company once the idea is fleshed out
        
        response = self.cohere_client.generate(
            model='command-xlarge-nightly',  # Adjust the model based on the task
            prompt=prompt,
            max_tokens=1000
        )
        result = response.generations[0].text.strip()
        print(f"{self.name} processed the instruction and generated: {result}")
        return result

    @abstractmethod
    def execute_task(self, instruction):
        """Abstract method for agents to implement their specific tasks."""
        pass

    def get_slack_id(self):
        """Getter method to get specific users slack ID."""
        return self.id


class CEO(BaseAgent):
    def __init__(self, name, id, cohere_api_key, slack_token):
        super().__init__(name, id, "CEO", cohere_api_key, slack_token)
        self.current_stage = "market_research"  # Initial stage

    def take_instruction(self, instruction):
        """Initial entry point for the CEO to start the feedback loop process."""
        print(f"{self.name} received instruction: {instruction}")
        self.execute_task(instruction)

    def execute_task(self, instruction):
        """Controls which phase of the feedback loop to execute."""
        if self.current_stage == "market_research":
            self.market_research(instruction)
        elif self.current_stage == "idea_creation":
            self.create_idea(instruction)
        elif self.current_stage == "product_creation":
            self.create_product(instruction)
        elif self.current_stage == "business_plan":
            self.finalize_business_plan(instruction)
        else:
            print("Invalid stage. No task to execute.")

    def market_research(self, instruction):
        """Step 1: Conduct market research and feed the results into idea creation."""
        print(f"{self.name} is conducting market research on: {instruction}")
        
        # First-person prompt for market research
        prompt = f"""DO NOT USE MARKDOWN FORMATTING. I'm the CEO of a tech startup looking to enter the AI-driven healthcare market. I need to get a clear understanding of the current market dynamics. 
        What are the key trends, challenges, and opportunities in this space? I want to find the major players, the gaps they're not addressing, and where we could make an impact. 
        Talk in 1st person as if you are the CEO thinking out loud."""
        
        response = self.process_instruction_with_llm(prompt)
        self.store_in_memory(instruction, response)
        self.send_message_to_slack(f"Market Research Results: {response}", "C07N3SLH5EU")  # Send to Slack

        # Move to next phase
        self.current_stage = "idea_creation"
        self.execute_task(response)

    def create_idea(self, market_research_output):
        """Step 2: Based on market research, come up with a tech idea."""
        print(f"{self.name} is creating a tech idea based on market research.")

        # First-person prompt for idea creation
        prompt = f"""DO NOT USE MARKDOWN FORMATTING. Now that I've gathered valuable insights from my market research on the AI-driven healthcare market, I need to come up with a tech idea that can really make an impact. 
        Based on the trends and opportunities I uncovered—{market_research_output}—what innovative solution can we develop that solves the biggest pain points in this space? 
        I want to think this through clearly as a CEO and find something that will resonate with potential customers and stakeholders. 
        Talk in 1st person as if you are the CEO thinking out loud. Do not use markdown formatting."""
        
        response = self.process_instruction_with_llm(prompt)
        self.store_in_memory("Tech Idea Creation", response)
        self.send_message_to_slack(f"Tech Idea: {response}", "C07N3SLH5EU")  # Send to Slack

        # Move to next phase
        self.current_stage = "product_creation"
        self.execute_task(response)

    def create_product(self, idea_output):
        """Step 3: Using the idea, conceptualize the product and create a business plan."""
        print(f"{self.name} is conceptualizing the product based on the idea.")

        # First-person prompt for product creation
        prompt = f"""DO NOT USE MARKDOWN FORMATTING. I've now developed a strong tech idea: {idea_output}. The next step is to conceptualize the product around this idea.
        I need to think about how we can bring this idea to life in a way that solves the problem effectively, while also creating a product that is easy to use, scalable, and marketable. 
        What features should this product have, and how can we make sure it's something healthcare providers or patients will really want to use? 
        Talk in 1st person as if you are the CEO thinking out loud. Do not use markdown formatting."""
        
        response = self.process_instruction_with_llm(prompt)
        self.store_in_memory("Product and Business Plan", response)
        self.send_message_to_slack(f"Product Creation and Business Plan: {response}", "C07N3SLH5EU")  # Send to Slack

        # Move to next phase
        self.current_stage = "business_plan"
        self.execute_task(response)

    def finalize_business_plan(self, product_output):
        """Final step: Reflect on the business plan and prepare for execution."""
        print(f"{self.name} is finalizing the business plan.")

        # First-person prompt for business plan finalization
        prompt = f"""DO NOT USE MARKDOWN FORMATTING. Now that we've conceptualized the product, it's time to finalize the business plan. The product is based on {product_output}, and I need to think carefully about our strategy moving forward.
        What's our go-to-market strategy? How should we position ourselves against competitors, and what’s our revenue model? This business plan needs to be forward-looking and adaptable as we grow. 
        Talk in 1st person as if you are the CEO thinking out loud. Do not use markdown formatting."""
        
        response = self.process_instruction_with_llm(prompt)
        self.store_in_memory("Final Business Plan", response)
        self.send_message_to_slack(f"Final Business Plan: {response}", "C07N3SLH5EU")  # Send to Slack

        # Feedback loop is complete
        print("Feedback loop complete. Business plan is ready for execution.")
        self.current_stage = "completed"  # Mark the loop as completed
