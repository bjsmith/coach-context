from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import yaml
from yaml.loader import SafeLoader
from socket import gethostname # do better
#from flask import Flask
from slack_bolt import App
import os

class ChatConfig:

    config = None

    def get_config(force_reload=False):

        if force_reload or ChatConfig.config is None:
            is_prod = os.environ.get('IS_HEROKU', None)=='True'
            if is_prod==True:
                print("loading config from heroku")
                #get all keys in the environment with os.environ
                all_environ = dict(os.environ)
                #now get the keys that start with "COACHCONTEXT_"
                coachcontext_environ = {k.replace("COACHCONTEXT_",""):v for k,v in all_environ.items() if k.startswith("COACHCONTEXT_")}
                ChatConfig.config = coachcontext_environ
                return ChatConfig.config


            with open('delivercbt_files/config.yml') as f:
                    all_yaml = yaml.load(f, Loader=SafeLoader)
                    if gethostname() in all_yaml.keys():
                        ChatConfig.config = all_yaml[gethostname()]
                    else:
                        ChatConfig.config = all_yaml['default']
        
        return ChatConfig.config

class CoachingIOInterface:
    """
    creates a mode-agnostic pattern for the therapist to use to communicate with the client
    """
    def __init__(self):
        raise NotImplementedError

    def send_message(self):
        raise NotImplementedError
    
    def indicate_response_coming(self):
        raise NotImplementedError

class AsyncCoachingIOInterface:
    """
    creates a mode-agnostic pattern for the therapist to use to communicate with the client
    """
    def __init__(self):
        raise NotImplementedError

    async def send_message(self):
        raise NotImplementedError
    
    def indicate_response_coming(self):
        raise NotImplementedError


class CBTTerminal(CoachingIOInterface):
    """
    manages input and output with the client.
    """
    # keep this as simple as possible; just input and output
    def __init__(self):
        os.system('clear')
        pass

    def send_message(self, message):
        self.print_output(message)

    def print_output(self, output_text):
        print("\nTherapist: \n" + output_text + "\n\n")

    def get_input(self, prompt_text=None):
        if prompt_text is not None:
            print(prompt_text)
        return input("You: \n")
    
    def indicate_response_coming(self):
        print("...")

