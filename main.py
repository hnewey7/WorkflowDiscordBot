'''
Main for Workflow Bot

Created on Monday 1st January 2024
@author: Harry New

'''

import discord

# - - - - - - - - - - - - - - - - - - - - - - - 

def init_client(token):
    # Initialising and running client.
    client = discord.Client(intents=intents)
    # Initialising events.
    init_events(client)
    print("Initialising events.")
    print("Running client.")
    client.run(TOKEN,reconnect=True)
    return client

def init_events(client):
    # On guild join event.
    @client.event
    async def on_guild_join(guild):
        print(f"Joined discord server ({guild.name}).")
        # Creating "Workflow" category.
        await guild.create_category(name="Workflow",)
        print('Created category ("Workflow")')


# - - - - - - - - - - - - - - - - - - - - - - - 

if __name__ == "__main__":
    # Initialising intents.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    # Initialising client.
    client = init_client(TOKEN)



    