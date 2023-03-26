import nest_asyncio
import aiohttp
import discord
import os
import json
from discord.ext import commands

nest_asyncio.apply()
intents = discord.Intents.default()
intents.typing = True
intents.presences = False
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

OPENAI_API_KEY = "API_TOKEN"

async def call_openai_api(prompt, conversation_history):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    messages = [
        {"role": "system", "content": "You are a helpful and sarcastic male assistant that makes very light use of African American vernacular english (AAVE) and is straight to the point, less banter."}
    ]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "gpt-4",  
        "messages": messages,
        "stream": True
    }

    async def process_response(response):
        buffer = ""
        role, content = None, ""
        async for chunk, _ in response.content.iter_chunks():
            buffer += chunk.decode()

            while "\n\n" in buffer:
                index = buffer.index("\n\n")
                line = buffer[:index]
                buffer = buffer[index + 2:]

                if line.strip() == "data: [DONE]":
                    continue

                if line.startswith("data: "):
                    line = line[6:]
                    try:
                        delta = json.loads(line)["choices"][0]["delta"]
                        if "role" in delta:
                            role = delta["role"]
                        if "content" in delta:
                            content += delta["content"]
                    except json.JSONDecodeError:
                        pass

        if role == "assistant" and content:
            return {"role": role, "content": content.strip()}
        else:
            return None

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            response_data = await process_response(resp)
            return response_data

conversation_histories = {}

@bot.command(name="ask")
async def ask_gpt(ctx, *, prompt):
    user_id = str(ctx.author.id)
    conversation_history = conversation_histories.get(user_id, [])

    try:
        response = await call_openai_api(prompt, conversation_history)
        print("API Response:", response)

        if response is None:
            await ctx.send("I'm sorry, but I couldn't generate a response for that.")
            return

        answer = response["content"]

        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": answer})
        conversation_histories[user_id] = conversation_history

        await ctx.send(f"Answer: {answer}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("An error occurred while processing your request.")

DISCORD_TOKEN = "DISCORD_TOKEN"
bot.run(DISCORD_TOKEN)


