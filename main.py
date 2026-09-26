import os
import logging
from flask import Flask
from threading import Thread
# Agar aap pyrogram ya telegram bot library use kar rahe hain, toh uska import yahan rahega
# Example: from pyrogram import Client

# Logging setup
logging.basicConfig(level=logging.INFO)

# --- 1. Flask Keep-Alive Server Setup ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is active 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 2. Main Bot Code Setup ---
def main():
    # Flask server ko background me start karein
    keep_alive()
    logging.info("Flask keep-alive server started successfully.")
    
    # Yahan par aap apne bot ko start karne ka code likhein
    # Jaise Pyrogram ke liye:
    # app_bot = Client("my_bot", api_id=..., api_hash=..., bot_token=...)
    # app_bot.run()
    
    print("Bot is running...")

if __name__ == "__main__":
    main()
