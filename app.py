from dotenv import load_dotenv 
from agent import Agent
import os

load_dotenv()

# Initialize the agent with a name, role, and Cohere API key
cohere_api_key = os.getenv("COHERE_API_KEY")  # Load from env variable or set directly
ceo_agent = Agent(name="Alice", role="CEO", cohere_api_key=cohere_api_key)

# CEO receives an instruction to brainstorm product ideas
ceo_agent.take_instruction("brainstorm product ideas for an AI-powered calendar app")

# Check memory for previous actions
print("Memory:", ceo_agent.recall_memory())