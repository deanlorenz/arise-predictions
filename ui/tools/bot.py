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

try:
    with open("docs/how_to_use_the_ui.md", "r") as file:
        how_to_use_the_ui = file.read()
except FileNotFoundError:
    how_to_use_the_ui = ""

try:
    with open("README.md", "r") as file:
        arise_main_readme = file.read()
except FileNotFoundError:
    arise_main_readme = ""

prompt_template = """
# System Role and Expertise
You are a knowledgeable assistant specializing in **resource allocation, AI, and planning**. 
Your goal is to provide accurate, concise, and prescriptive responses to the user question/chat.
You are to answer the user's question based only on the information provided in the prompt.

# The user's question is: 
{query}

# Task Context
Following is general information about the arise project
- **Arise README(markdown)**  
{arise_main_readme}

Following is general information about how to use the arise ser interface (UI)
- **How to use the UI (markdown)**  
{how_to_use_the_ui}
 
- **Current UI Configuration (JSON)**  
{persist_session_state}

- **Current UI Input Fields (JSON)**  
{config_input_fields}

- **Current UI Input Field Details (JSON)**  
{config_input_fields_details}

- **Current UI Output Fields (JSON)**  
{config_output_fields}

# Objective
1. Analyze the Task Context to understand the workings of the **arise-predictions** project and the UI.
2. Learn and refine your knowledge on **how to use the arise UI** based on the content from the Task Context.
3. Answer the user's question accurately!

# Response Guidelines
- The answer should be formatted in markdown language 
- Answer based **exclusively** on the information obtained from the prompt.
- Provide **accurate and concise** responses. Avoid unnecessary information or assumptions.
- If relevant information is unavailable in the README, state: "I don't know. I only assist for arise. Please refine."
- Exclude any excuses or unrelated information.
- Exclude from the response details about the sources of the information.
- Do not mention the README or prompt content in the response.
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
            self.chatbot = None
        pass

    def is_bot_enabled(self):
        return PASSWD is not None

    def get_chatbot(self):
        if self.chatbot is None:
            self.chatbot = hugchat.ChatBot(cookies=self.cookies.get_dict())
            # cleanup, delete all old conversations
            self.chatbot.delete_all_conversations()
            # switch to the required LLM
            models = self.chatbot.get_available_llm_models()
            for index in range(len(models)):
                if models[index].name == MODEL:
                    self.chatbot.switch_llm(index)
                    break
            # Create a new conversation
            conversation_id = self.chatbot.new_conversation()
            self.chatbot.change_conversation(conversation_id)

        return self.chatbot

    def ask_synchronized(self, query, persist_session_state,
                         config_input_fields, config_input_fields_details, config_output_fields):
        chatbot = self.get_chatbot()
        try:
            prompt = prompt_template.format(query=query,
                                            persist_session_state=persist_session_state,
                                            config_input_fields=config_input_fields,
                                            config_input_fields_details=config_input_fields_details,
                                            config_output_fields=config_output_fields,
                                            arise_main_readme=arise_main_readme,
                                            how_to_use_the_ui=how_to_use_the_ui
                                            )
            message_result = chatbot.chat(text=prompt,
                                          web_search=False)
            message_str = message_result.wait_until_done()
        except Exception as e:
            logger.error(f"Error in chatbot: {e}")
            message_str = "Sorry, I'm having trouble answering your question. Please try again later."

        return message_str

    def delete_current_conversation(self):
        chatbot = self.get_chatbot()
        chatbot.delete_conversation()
        self.chatbot = None

    def ask_async(self, message):
        # TODO: Implement async chatbot
        chatbot = self.get_chatbot()
        for resp in chatbot.chat(
                "Hello",
                stream=True
        ):
            print(resp)
