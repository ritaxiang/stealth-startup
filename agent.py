import openai

class Agent:
    def __init__(self, name, role, llm_api_key):
        self.name = name  # e.g., "CEO"
        self.role = role  # e.g., "Chief Executive Officer"
        self.llm_api_key = llm_api_key
        self.memory = []  # Memory to store previous actions or responses

    def take_instruction(self, instruction):
        """Takes an instruction or task as input and processes it."""
        print(f"{self.name} received instruction: {instruction}")
        response = self._process_with_llm(instruction)
        self._execute_action(response)

    def _process_with_llm(self, instruction):
        """Uses an LLM (e.g., OpenAI) to process the instruction and generate a response."""
        openai.api_key = self.llm_api_key
        prompt = f"As the {self.role}, {instruction}"
        
        # Example of calling the OpenAI API (assuming GPT-4)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        result = response['choices'][0]['text'].strip()
        
        print(f"{self.name} processed the instruction and generated: {result}")
        return result

    def _execute_action(self, response):
        """Executes the generated response (e.g., posting to Slack, saving to DB)."""
        # This could involve posting a message to Slack or triggering another action.
        print(f"{self.name} is executing: {response}")
        
        # Optional: Store the action and response in memory for later
        self.memory.append({"instruction": response, "action": response})

    def recall_memory(self):
        """Recalls previous actions and responses from memory."""
        return self.memory
    
