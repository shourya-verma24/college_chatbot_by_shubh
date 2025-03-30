import os
import discord
import nltk
import threading
import asyncio
from flask import Flask, render_template, request
from dotenv import load_dotenv  # Load environment variables
from nltk.chat.util import Chat, reflections
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Get the token securely

# Define chatbot responses
pairs = [
    [r"hi|hello|hey", ["Hello! How can I assist you today?"]],
    [r"(.*)admission(.*)", ["Admission details are available on our website."]],
    [r"(.*)courses(.*)", ["We offer B.Tech, M.Tech, MBA, and PhD programs."]],
    [r"(.*)fees(.*)", ["The fee structure varies by course. Please check our finance section."]],
    [r"(.*)library(.*)", ["The library is open from 9 AM to 7 PM on weekdays."]],
    [r"bye|goodbye", ["Goodbye! Have a great day!"]],
    [r"(.*)", ["I'm not sure about that. Please contact the college helpdesk."]]
]

chatbot = Chat(pairs, reflections)

# Flask app setup
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["GET"])
def chatbot_response():
    user_message = request.args.get("msg")
    response = chatbot.respond(user_message)
    return response

# Discord bot setup using commands.Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    response = chatbot.respond(message.content)
    await message.channel.send(response)

# Function to run Flask
def run_flask():
    app.run(debug=True, use_reloader=False)

# Function to run Discord bot asynchronously
async def run_discord_bot():
    await bot.start(TOKEN)  # Now the token is hidden

# Run both Flask and Discord bot simultaneously
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_discord_bot())
