# bot.py
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

def role_to_give(pp):
    if pp >= 10000:
        return "Patrician"
    if pp >= 7000:
        return "Grandmaster"
    if pp >= 5000:
        return "Senior Master"
    if pp >= 3000:
        return "Master"
    if pp >= 2000:
        return "Expert"
    if pp >= 1000:
        return "Advanced"
    if pp >= 500:
        return "Intermediate"
    if pp >= 200:
        return "Beginner"
    return "Plebeian"

def find(roles, name):
    for role in roles:
        if role.name == name:
            return role

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
farmers = ["Sotarks", "browiec", "UndeadCapulet", "Lami", "Log Off Now", "apladobi",
           "Akitoshi", "Doormat", "fieryrage", "Monstrata", "Nevo", "Seni", "Kyuukai", "Taeyang"]
@client.event
async def on_message(message):
    if message.content == ">osu" and message.channel.name == "role-update":
        owomsg = await client.wait_for("message")
        if owomsg.author.name == 'owo':
            osustats = owomsg.embeds[0].description
            pp = float(osustats[osustats.find("PP"):osustats.find("Acc")].strip("*P: ").replace(',', ''))
            role = find(message.guild.roles, role_to_give(pp))
            if role not in message.author.roles:
                await message.author.add_roles(role)
                await message.channel.send(message.author.name + " is now a " + role.name + ".")
            else:
                await message.channel.send(message.author.name + " is already a " + role.name +
                                           ". Get better before you try again. Go farm some " + random.choice(farmers) + ".")



client.run(TOKEN)