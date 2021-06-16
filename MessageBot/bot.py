# bot.py
import os
import datetime
import asyncio

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

task_dict = {}
days = [1,2,3]

def find(roles, name):
    for role in roles:
        if role.name == name:
            return role

def find_all_tasks(plugin_name, user):
    taskkeys = []
    for key in task_dict.keys():
        if key[0] == plugin_name and key[2] == user:
            taskkeys.append(key)
    return taskkeys

def all_users_with_role(members,role):
    users = []
    for user in members:
        if role in user.roles:
            users.append(user)
    return users

async def plugin_reminder(plugin_name, days_before, user):
    await user.create_dm()
    if days_before == 1:
        await user.dm_channel.send("The plugin " + plugin_name + " is due in " + str(days_before) + " day. Here is a friendly reminder.")
    else:
        await user.dm_channel.send("The plugin " + plugin_name + " is due in " + str(days_before) + " days. Here is a friendly reminder.")
    return

async def plugin_reminder_task(plugin_name, days_before, user, date_to_remind):
    now = datetime.datetime.now()
    await asyncio.sleep((date_to_remind - now).total_seconds())
    await plugin_reminder(plugin_name,days_before,user)
    global task_dict
    task_dict[(plugin_name,days_before,user, date_to_remind)].cancel()
    task_dict.pop((plugin_name,days_before,user, date_to_remind),None)
    return

def set_reminder_task(plugin_name, days_before, user, date_to_remind):
    task = client.loop.create_task(plugin_reminder_task(plugin_name, days_before, user, date_to_remind))
    global task_dict
    task_dict[(plugin_name, days_before, user, date_to_remind)] = task

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    #-message (role) message command
    if message.content.startswith("-message"):
        #parse message
        args = message.content[8:]
        if len(args) < 2:
            await message.channel.send("You have not entered the command correctly. Command: -message (role) message_to_write")
            return
        if args[1] != '(' or args.find(')') == -1:
            await message.channel.send("You have not entered the command correctly. There must be parentheses around the role to ping. Command: -message (role) message_to_write")
            return
        role_string = args[2:args.find(')')]
        if len(args) == (args.find(')') + 1):
            await message.channel.send("You have not entered the command correctly. You have not written a message. Command: -message (role) message_to_write")
            return
        if args[args.find(')') + 1] != ' ' or len(args) == (args.find(')') + 2):
            await message.channel.send("You have not entered the command correctly. You must have a space between the role and the message. Command: -message (role) message_to_write")
            return
        message_to_send = args[args.find(')') + 2:]

        role_object = find(message.guild.roles,role_string)
        users_to_message = all_users_with_role(message.guild.members,role_object)
        for member in users_to_message:
            await member.create_dm()
            await member.dm_channel.send(message_to_send)

    # -task @person plugin name date     (date must always be mm/dd/yyyy)
    if message.content.startswith("-task"):
        args = message.content[5:]
        if len(args) < 2:
            await message.channel.send("You have not entered the command correctly. Command: -task @person (plugin name) date")
            return
        if not message.mentions or args[2] != "@":
            await message.channel.send("You have not mentioned anyone right after the command (with one space between task and @). Command: -task @person (plugin name) date")
            return
        person = message.mentions[0]
        if args.find('(') == -1 or args.find(')') == -1:
            await message.channel.send("You have not entered the plugin correctly. There must be parentheses around the plugin. Command: -task @person (plugin name) date")
            return
        plugin_name = args[args.find('(') + 1 : args.find(')')]
        if len(args) == (args.find(')') + 1):
            await message.channel.send("You have not entered the command correctly. You have not written a date. Command: -task @person (plugin name) date")
            return
        if args[args.find(')') + 1] != ' ' or len(args) == (args.find(')') + 2):
            await message.channel.send("You have not entered the command correctly. You must have a space between the plugin name and the date. Command: -task @person (plugin name) date")
            return
        deadline_date = args[args.find(')') + 2:]
        if not (deadline_date[:2].isnumeric() and deadline_date[2] == '/' and deadline_date[3:5].isnumeric() and deadline_date[5] == '/' and deadline_date[6:].isnumeric() and len(deadline_date) == 10):
            await message.channel.send("You have not entered a correct date. It must be in the form mm/dd/yyyy. Command: -task @person (plugin name) date")
            return

        now = datetime.datetime.now()
        curtime = now.time().strftime('%H:%M:%S')
        format_str = '%m/%d/%Y %H:%M:%S'  # The format
        datetime_obj = datetime.datetime.strptime(deadline_date + " " + curtime, format_str)

        for day in days:
            #create reminder date
            reminder_date = datetime_obj - datetime.timedelta(days=day)
            today = datetime.date.today()

            if reminder_date.date() < today:
                await message.channel.send("The " + str(day) + " day reminder cannot be sent as that day has already passed")
                return
            elif reminder_date.date() == today:
                await plugin_reminder(plugin_name,day,person)
                await message.channel.send("The " + str(day) + " day reminder has been sent")
                return
            else:
                set_reminder_task(plugin_name,day,person,reminder_date)
                await message.channel.send("The " + str(day) + " day reminder has been scheduled for " + reminder_date.strftime('%m/%d/%Y') + ".")
    #UNTESTED
    if message.content == "-listtasks":
        if len(task_dict.keys()) == 0:
            await message.channel.send("There are no scheduled tasks")
            return
        else:
            await message.channel.send("Here are the list of tasks currently scheduled")
        for key in task_dict.keys():
            await message.channel.send("The " + str(key[1]) + " day reminder for plugin " + str(key[0]) + " has been scheduled for user " + str(key[2]) + " and is due on " + key[3].strftime('%m/%d/%Y') + ".")

    # -untask @person plugin name     (date must always be mm/dd/yyyy)
    if message.content.startswith("-untask"):
        args = message.content[7:]
        if len(args) < 2:
            await message.channel.send("You have not entered the command correctly. Command: -untask @person (plugin name)")
            return
        if not message.mentions or args[2] != "@":
            await message.channel.send("You have not mentioned anyone right after the command (with one space between untask and @). Command: -untask @person (plugin name)")
            return
        person = message.mentions[0]
        if args.find('(') == -1 or args.find(')') == -1:
            await message.channel.send("You have not entered the plugin correctly. There must be parentheses around the plugin. Command: -untask @person (plugin name)")
            return
        plugin_name = args[args.find('(') + 1 : args.find(')')]

        tasks_to_cancel = find_all_tasks(plugin_name,person)

        for taskkey in tasks_to_cancel:
            task_dict[taskkey].cancel()
            task_dict.pop(taskkey, None)

        await message.channel.send("The reminder for plugin " + plugin_name + " for user " + str(person) + " has been canceled.")

client.run(TOKEN)