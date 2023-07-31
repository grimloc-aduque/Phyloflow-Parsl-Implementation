
import json

import openai
from function_calls import *

# Include here your OpenAI API Key

openai.api_key = 'YOUR-API-KEY'


class OpenAIAgent:

    def __init__(self, functions) -> None:
        self.functions = functions
        self.messages = None
        self.response = None
        self.response_message = None
        self.GREEN_COLOR = '\033[92m'
        self.END_COLOR = '\033[0m'
        self.context = '''
    If you are asked to execute one single task receive file names
    If you are asked to execute multiple tasks:
        Receive file names for the first task
        Send the future ids to the other tasks'''

    def start_conversation(self, msg:str):
        self.messages = []
        self.add_context()
        next_msg = msg
        while True:
            self.ask_openai(next_msg)
            if self.is_last_function_call():
                break
            future_id = self.execute_function_call()
            next_msg = f"Task scheduled with AppFuture id: {future_id} '\nNow what?"
        print(f"\nDONE\n")

    def ask_openai(self, msg:str):
        self.add_user_msg(msg)
        print(f"\n{self.GREEN_COLOR}User: {msg}{self.END_COLOR}")
        self.response =  openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=self.messages,
            functions=self.functions,
            function_call='auto',
            temperature=0
        )   
        self.add_ai_message()
        
    def is_last_function_call(self):
        finish_reason = self.response['choices'][0]['finish_reason']
        return finish_reason == 'stop'

    def execute_function_call(self):
        function_name = self.response_message['function_call']['name']
        fuction_to_call = globals()[function_name]
        function_args = json.loads(self.response_message['function_call']['arguments'])

        print("\nFunction Calling")
        print("Function Name: ", function_name)
        print("Function Args: ", function_args)

        return fuction_to_call(**function_args)

    # Messages

    def add_context(self):
        self.add_user_msg(self.context)
        print(f"\n{self.GREEN_COLOR}Context: {self.context}{self.END_COLOR}")

    def add_user_msg(self, content:str):
        self.messages.append(
            {
                'role': 'user', 
                'content': content
            }
        )
    
    def add_ai_message(self):
        self.response_message = self.response['choices'][0]['message']
        self.messages.append(self.response_message.to_dict())
