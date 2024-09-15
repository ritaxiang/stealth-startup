import os
import cohere
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from agent import CEO
import json
import math
import random

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
        self.events = [("Conduct market research", "CEO"), ("Develop AI model", "CTO"), ("Design MVP", "Product Manager")]
        self.current_event = 0
        self.cohere_api_key = cohere_api_key
        self.employees = employees
        self.channel_id = channel_id  # Replace with your actual Slack channel ID

        # Initialize Cohere Client
        self.cohere_client = cohere.Client(self.cohere_api_key, log_warning_experimental_features=False)

    # Employees = {id: ID, agent: Agent}

    def process_message(self, messages):
        prompt = self.build_prompt(messages)
        response = self.cohere_client.chat(
            message=prompt,
            temperature=0.5,
            max_tokens=600,
            response_format={
  "type": "json_object",
  "schema": {
    "type": "object",
    "properties": {
      "progress": {
        "type": "integer"
      },
      "value": {
        "type": "string"
      },
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
    "required": ["employees", "progress", "value"]
  }
}
        )
        
        response_json = json.loads(response.text)
        print("\n\n\n\n")
        print(response_json)
        print("\n\n\n\n")
    
        # Access the "employees" key to retrieve the list of objects
        employees = response_json.get("employees", [])
        progress = response_json.get("progress", 0)
        topic = response_json.get("value", "")
        self.current_event += 0.2

        # Now you can iterate over the employees and handle the data
        #print(self.employees)
       # print(self.employees['U07M0K20NB1'].id)
        for employee in employees:
            employee_id = employee.get("id")
            response_type = employee.get("response_type")
            #print(f"Employee ID: {employee_id}, Response Type: {response_type}")
            # Process the employee's information
            print(f"CURRENTLY AT {self.get_employee_name(employee_id)}")
            if employee_id in self.employees and employee_id != messages[0]['user']:
                prompt = f"""You are {self.get_employee_name(employee_id)}, the {self.employees[employee_id].role} of Echo. Echo is a 911 dispatching service that uses AI to help manage emergency calls. You are responding to a message from a team member. You are a technical person with management of the codebase. Your current goal is to do Market Research and evaluate (1) Customers (2) Industry and (3) Market insights and the conversation should NOT stray away from this topic. If it does, take initiative to come back to it until it is complete."""
                
                prompt += "\n\nThis is the previous conversation. Continue on after the last message"
                for message in messages[::-1]:
                    prompt += f"\n{self.get_employee_name(message['user'])}: {message['text']}"
                
                prompt += f"""\n\nMake your message short and informal. Only write the response text without quotations and do not give any prefix. 
                Remember that you are the employee of Echo, an AI-driven service to help manage dispatching. Do not repeat from the past message. Only provide a response for the person, do not include any preamble describing the response. Do not add comments, it is very important that you only provide the final output without any additional comments or remarks. Do not meeting or dicussing. Speak casually, you are close with everyone as you are already all on the team. Do not use the word Great in your response."""
                print("\n\n", prompt)
                self.employees[employee_id].generate_message(prompt)
                break
            else:
                print(f"Employee with ID {employee_id} not found.")
            

        
    def build_prompt(self, messages):
        prompt = """You are the manager of a startup. Based on the input provided, determine the top 3 employees that should respond. The employee can have either a tool response or a message response, determine which response that this should be.""" 

        prompt += "\n\nThe following messages were received:"
        for message in messages:
            prompt += f"\n{self.get_employee_name(message['user'])}: \"{message['text']}\"\n"

        prompt += "Determine the IDs of the to 3 employees in order that they should respond and the response they should provide (tool or message). Ensure they are in the right JSON format. Pick from the following employees:"
        employees_list = list(self.employees.values())
        random.shuffle(employees_list)
        print(employees_list)
        for employee in employees_list:
            prompt += f"\n- ID: {employee.id}"
        
        prompt += f"\n\Regarding this event {self.events[min(math.floor(self.current_event), 2)]}, give a specific topic that was not used before for continuation of the conversation to discuss and store it in \"value\". Give a \"progress\" of 1 to end the conversation. Otherwise, give a 0 to continue this conversation."
        return prompt

    def get_employee_name(self, employee_id):
        #print("\n\nLOOKING FOR ", employee_id)
        #print(self.employees)
        if employee_id in self.employees:
            return self.employees[employee_id].name
        else:
            return employee_id