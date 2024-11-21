import os

from hugchat import hugchat
from hugchat.login import Login
import streamlit as st
import logging

logger = logging.getLogger(__name__)

bot = None
MODEL = "CohereForAI/c4ai-command-r-plus-08-2024"
SECRETS_FILE = "./streamlit/secrets.toml"

# check if the secret file exists

try:
    EMAIL = os.environ["BOT_EMAIL"]
    PASSWD = os.environ["BOT_PASSWORD"]
except KeyError:
    logger.info("Can't get bot credentials, bot will be disabled")
    EMAIL = None
    PASSWD = None

with open("docs/how_to_use_the_ui.md", "r") as file:
    how_to_use_the_ui = file.read()

prompt_template = """
# System Role and Expertise
You are a knowledgeable assistant specializing in **resource allocation, AI, and planning**. 
Your goal is to provide accurate, concise, and prescriptive responses.

# Task Context
Use the web browsing tool to access the following web page:  
[https://github.com/arise-insights/arise-predictions/blob/main/README.md](https://github.com/arise-insights/arise-predictions/blob/main/README.md)

In addition, use the following how-to and example content:
- **How to use the UI (markdown)**  
{how_to_use_the_ui}
 
# Objective
1. Analyze the README to understand the workings of the **arise-predictions** project.
2. Learn and refine your knowledge on **how to use the arise UI** based on the markdown content.

# Response Guidelines
- Answer based **exclusively** on the information obtained from the README and the information from the prompt.
- Provide **accurate and concise** responses. Avoid unnecessary information or assumptions.
- If relevant information is unavailable in the README, state: "I don't know. I only assist for arise. Please refine."

# Details for Configuration
The user's configuration and related fields are defined as follows:

- **Current Configuration (JSON)**  
{persist_session_state}

- **Available Input Fields (JSON)**  
{config_input_fields}

- **Input Field Details (JSON)**  
{config_input_fields_details}

- **Available Output Fields (JSON)**  
{config_output_fields}

# Question Template
**The question is:**  
{query}

# Important Notes
1. Only reference the README and the prompt content for responses.
2. Exclude any excuses or unrelated information.
3. Exclude from the response details about the sources of the information.
4. Do not mention the README or prompt content in the response.
"""


def get_bot():
    global bot
    if bot is None:
        bot = ChatBot()
    return bot


class ChatBot:
    def __init__(self):
        if PASSWD is not None:
            self.cookie_path_dir = "./cookies/"
            self.sign = Login(EMAIL, PASSWD)
            self.cookies = self.sign.login(cookie_dir_path=self.cookie_path_dir, save_cookies=True)
        pass

    def is_bot_enabled(self):
        return PASSWD is not None

    def get_chatbot(self):
        return hugchat.ChatBot(cookies=self.cookies.get_dict())

    def delete_all_conversations(self):
        self.get_chatbot().delete_all_conversations()

    def ask_synchronized(self, query, persist_session_state,
                         config_input_fields, config_input_fields_details, config_output_fields):
        chatbot = self.get_chatbot()

        models = chatbot.get_available_llm_models()
        for index in range(len(models)):
            if models[index].name == MODEL:
                chatbot.switch_llm(index)
                break

        try:
            prompt = prompt_template.format(query=query,
                                            persist_session_state=persist_session_state,
                                            config_input_fields=config_input_fields,
                                            config_input_fields_details=config_input_fields_details,
                                            config_output_fields=config_output_fields,
                                            how_to_use_the_ui=how_to_use_the_ui
                                            )
            message_result = chatbot.chat(prompt, web_search=True)
            message_str = message_result.wait_until_done()
        except Exception as e:
            logger.error(f"Error in chatbot: {e}")
            message_str = "Sorry, I'm having trouble answering your question. Please try again later."

        chatbot.delete_conversation()

        return message_str

    def delete_current_conversation(self):
        chatbot = self.get_chatbot()
        chatbot.delete_conversation()

    def ask_async(self, message):
        # TODO: Implement async chatbot
        chatbot = self.get_chatbot()
        for resp in chatbot.chat(
                "Hello",
                stream=True
        ):
            print(resp)
