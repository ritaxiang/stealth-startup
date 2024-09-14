from agent import Agent

# Initialize the agent with a name, role, and OpenAI API key
ceo_agent = Agent(name="Alice", role="CEO", llm_api_key="your-openai-api-key")

# CEO receives an instruction to brainstorm product ideas
ceo_agent.take_instruction("brainstorm product ideas for an AI-powered calendar app")

# Check memory for previous actions
print("Memory:", ceo_agent.recall_memory())