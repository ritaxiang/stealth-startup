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

    def send_message_to_slack(self, message, channel):
        """Send a message to Slack using the Slack SDK."""
        try:
            response = self.slack_client.chat_postMessage(
                channel=channel,
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
        prompt = f"As the {self.role} of a company, {instruction}" # TODO: have some way to expand on the company once the idea is fleshed out
        
        response = self.cohere_client.generate(
            model='command-xlarge-nightly',  # Adjust the model based on the task
            prompt=prompt,
            max_tokens=150
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