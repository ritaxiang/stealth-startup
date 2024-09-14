import os
import cohere

class Agent:
    def __init__(self, name, role, cohere_api_key):
        self.name = name  # e.g., "CEO"
        self.role = role  # e.g., "Chief Executive Officer"
        self.cohere_api_key = cohere_api_key
        self.memory = []  # Memory to store previous actions or responses
        
        # Initialize Cohere Client
        self.cohere_client = cohere.Client(self.cohere_api_key)

    def take_instruction(self, instruction):
        """Takes an instruction or task as input and processes it."""
        print(f"{self.name} received instruction: {instruction}")
        response = self._process_with_llm(instruction)
        self._execute_action(response)

    def _process_with_llm(self, instruction):
        """Uses the Cohere LLM to process the instruction and generate a response."""
        prompt = f"As the {self.role}, {instruction}"
        
        # Call Cohere's generate API
        response = self.cohere_client.generate(
            model='command-xlarge-nightly',  # You can adjust the model based on your need
            prompt=prompt,
            max_tokens=150
        )
        
        result = response.generations[0].text.strip()
        print(f"{self.name} processed the instruction and generated: {result}")
        return result

    def _execute_action(self, response):
        """Executes the generated response (e.g., posting to Slack, saving to DB)."""
        print(f"{self.name} is executing: {response}")
        
        # Optional: Store the action and response in memory for later
        self.memory.append({"instruction": response, "action": response})

    def recall_memory(self):
        """Recalls previous actions and responses from memory."""
        return self.memory