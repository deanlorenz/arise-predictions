from hugchat import hugchat
from hugchat.login import Login
import streamlit as st

EMAIL = st.secrets.bot.EMAIL
PASSWD = st.secrets.bot.PASSWD
MODEL = "CohereForAI/c4ai-command-r-plus-08-2024"

bot = None

prompt_template = """
You are a helpful assistant. 
You are an expert in resource allocation, AI and planning.
Use the web_search tool to read the content 
of the web page https://github.com/arise-insights/arise-predictions/blob/main/README.md 
and learn how the arise project works.

Answer the question based only on what you read from the web and the arise project.
Think step by step before answering.
The question is:
{query}

Answer accurate and concise without any unnecessary information.
Answer just from the web page and if content doesn't exist on the web page just emit the info.
Dont emit excuses, just information and if you don't know the answer just say you don't know.
"""


def get_bot():
    global bot
    if bot is None:
        bot = ChatBot()
    return bot


class ChatBot:
    def __init__(self):
        self.cookie_path_dir = "./cookies/"
        self.sign = Login(EMAIL, PASSWD)
        self.cookies = self.sign.login(cookie_dir_path=self.cookie_path_dir, save_cookies=True)
        pass

    def get_chatbot(self):
        return hugchat.ChatBot(cookies=self.cookies.get_dict())

    def delete_all_conversations(self):
        self.get_chatbot().delete_all_conversations()

    def ask_synchronized(self, query):
        chatbot = self.get_chatbot()

        models = chatbot.get_available_llm_models()
        for index in range(len(models)):
            if models[index].name == MODEL:
                chatbot.switch_llm(index)
                break

        prompt = prompt_template.format(query=query)
        message_result = chatbot.chat(prompt, web_search=True)
        message_str = message_result.wait_until_done()

        self.delete_current_conversation()

        return message_str

    def delete_current_conversation(self):
        chatbot = self.get_chatbot()
        chatbot.delete_conversation()

    def ask_async(self, message):
        chatbot = self.get_chatbot()
        for resp in chatbot.chat(
                "Hello",
                stream=True
        ):
            print(resp)
