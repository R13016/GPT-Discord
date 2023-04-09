%%writefile discord_bot.py

import nest_asyncio
nest_asyncio.apply()
import discord
import os
import requests
import json
from discord.ext import commands

# Set up the Discord bot
intents = discord.Intents.default()
intents.typing = True
intents.presences = False
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace this with your actual OpenAI API key
OPENAI_API_KEY = "Enter your openai api key here"

# Helper function to make OpenAI API requests
def call_openai_api(prompt, conversation_history):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    messages = [
        {"role": "system", "content": "You are a helpful and sarcastic assistant."}
    ]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "gpt-4",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

conversation_histories = {}

# Command to call the OpenAI API
@bot.command(name="ask")
async def ask_gpt(ctx, *, prompt):
    user_id = str(ctx.author.id)
    conversation_history = conversation_histories.get(user_id, [])

    try:
        response = call_openai_api(prompt, conversation_history)
        answer = response["choices"][0]["message"]["content"]

        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": answer})
        conversation_histories[user_id] = conversation_history

        await ctx.send(f"Answer: {answer}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("An error occurred while processing your request.")

# Replace this with your actual Discord bot token
DISCORD_TOKEN = "Enter your discord token here"

# Start the bot
bot.run(DISCORD_TOKEN)
