# -*- coding: utf-8 -*-

import logging

import telegram, os
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters



#################
import openai
	
openai.api_key = os.getenv("OPENAI_API_KEY") 
chat_language = os.getenv("INIT_LANGUAGE", default = "zh") #amend here to change your preset language
conversation = [{"role": "system", "content": os.getenv("OPENAI_ROLE_SYSTEM", default = "Your are a smart assistant")}]

class ChatGPT:  
    def __init__(self):  
        self.messages = conversation
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")

        # 其他可控参数
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0.5))
        self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0.6))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 500))
        self.role_system = os.getenv("OPENAI_ROLE_SYSTEM", default = "Your are a smart assistant")
        self.memory = int(os.getenv("OPENAI_MEMORY", default = 10))



    def get_response(self, user_input):
        #一旦超过memory长度（n次对话），则清空conversation，只保留system
        if len(self.messages) >= self.memory:
            conversation = [{"role": "system", "content": self.role_system}]

        conversation.append({"role": "user", "content": user_input})
        
        response = openai.ChatCompletion.create(
	            model=self.model,
                messages = self.messages
                )

        conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        
        print("AI回答內容：")        
        print(response['choices'][0]['message']['content'].strip())
        
        return response['choices'][0]['message']['content'].strip()
	







#####################

telegram_bot_token = str(os.getenv("TELEGRAM_BOT_TOKEN"))



# Load data from config.ini file
#config = configparser.ConfigParser()
#config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=telegram_bot_token)



@app.route('/callback', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'
      

def reply_handler(bot, update):
    """Reply message."""
    #text = update.message.text
    #update.message.reply_text(text)
    chatgpt = ChatGPT()        
    
                                            #update.message.text 人類的問題 the question humans asked
    ai_reply_response = chatgpt.get_response(update.message.text) #ChatGPT產生的回答 the answers that ChatGPT gave
    
    update.message.reply_text(ai_reply_response) #用AI的文字回傳 reply the text that AI made

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)