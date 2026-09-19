import os
import discord
from dotenv import load_dotenv
from agent import agent

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        try:
            content = message.content
            # Invoke the agent passing the active context dictionary cleanly
            response = await agent.ainvoke(
                {"messages": [("user", content)]},
                discord_message=message
            )
            
            last_message = response["messages"][-1]
            if isinstance(last_message, dict):
                agent_message = last_message.get("content", "").strip()
            else:
                agent_message = getattr(last_message, "content", str(last_message)).strip()
            
            # Send conversational responses directly back to Discord
            if agent_message and not agent_message.startswith("Image successfully generated"):
                if len(agent_message) > 2000:
                    for i in range(0, len(agent_message), 2000):
                        await message.channel.send(agent_message[i:i+2000])
                else:
                    await message.channel.send(agent_message)
                
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")

client.run(os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_API_KEY"))
