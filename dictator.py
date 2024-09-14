import os
import cohere
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agent import CEO
import json

""" 
load_dotenv()

# Initialize the Slack WebClient with Bot User OAuth Token
slack_token = os.getenv("IAN_K_SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

# Initialize the agent
cohere_api_key = os.getenv("COHERE_API_KEY")
ceo_agent = Agent(name="Alice", role="CEO", cohere_api_key=cohere_api_key) """

class Dictator:
    def __init__(self, name, cohere_api_key, employees, channel_id):
        self.cohere_api_key = cohere_api_key
        self.employees = employees
        self.channel_id = channel_id  # Replace with your actual Slack channel ID

        # Initialize Cohere Client
        self.cohere_client = cohere.Client(self.cohere_api_key)

    # Employees = {id: ID, agent: Agent}

    def process_message(self, messages):
        prompt = self.build_prompt(messages)
        response = self.cohere_client.chat(
            message=prompt,
            temperature=0.5,
            max_tokens=200,
            response_format={
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "employees": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string"
                        },
                        "response_type": {
                            "type": "string"
                        }
                    },
                    "required": ["id", "response_type"]
                }
            }
        },
        "required": ["employees"]
    }
}
        )
        response_json = json.loads(response.text)
        #print(response_json)
    
        # Access the "employees" key to retrieve the list of objects
        employees = response_json.get("employees", [])
        
        # Now you can iterate over the employees and handle the data
        #print(self.employees)
       # print(self.employees['U07M0K20NB1'].id)
        for employee in employees:
            employee_id = employee.get("id")
            response_type = employee.get("response_type")
            #print(f"Employee ID: {employee_id}, Response Type: {response_type}")
            # Process the employee's information
            if employee_id in self.employees:
                prompt = f"""This is the current conversation, continue the conversation by responding to the last message. """
                for message in messages[::-1]:
                    prompt += f"\n- {self.get_employee_name(employee_id)}: {message['text']}"
                
                prompt += "\n\nMake your message conversational and format the text like a normal chat response. Only write the response text without quotations and do not give any prefix. Feel free to end or continue the conversation"""

                self.employees[employee_id].generate_message(prompt)
            else:
                print(f"Employee with ID {employee_id} not found.")
            

        
    def build_prompt(self, messages):
        prompt = """You are the manager of a startup. Based on the input provided, determine the top 3 employees that should respond. The employee can have either a tool response
        or a message response, determine which response that this should be. You have the following employees. Pick only from the following employees:""" 

        for employee in self.employees.values():
            prompt += f"\n- {employee.id}: {employee.role}"

        prompt += "\n\nThe following messages were received:"
        for message in messages:
            prompt += f"\n{{\"role\": \"{message['user']}\", \"message\": \"{message['text']}\"}}\n"

        prompt += "Determine the IDs of the to 3 employees that should respond and the response they should provide (tool or message). Ensure they are in the right JSON format. Pick from the following employees:"
        for employee in self.employees.values():
            prompt += f"\n- {employee.id}: {employee.role}"
        return prompt

    def get_employee_name(self, employee_id):
        if employee_id in self.employees:
            return self.employees[employee_id].name
        else:
            return employee_id

if __name__ == "__main__":
    channel_id = "C07N3SLH5EU"  # Replace with your actual Slack channel ID
    messages = []
    try:
        response = client.conversations_history(channel=channel_id, limit=10)
        messages = response['messages']
    except SlackApiError as e:
        print(f"Error retrieving messages: {e.response['error']}")
        messages = []

    employee_map = {
        'U07M0K20NB1': ceo_agent,
    }
    Dictator("Dictator", cohere_api_key, employee_map).process_message(messages)

