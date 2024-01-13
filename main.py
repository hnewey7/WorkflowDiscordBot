'''
Main for Workflow Bot

Created on Monday 1st January 2024
@author: Harry New

'''

import discord
import logging
from datetime import datetime

# - - - - - - - - - - - - - - - - - - - - - - - 

def init_logging():
    # Creating log file name.
    start_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    log_file_name = "\\logs\\" + start_time + ".log"
    
    # Creating logger.
    global logger
    logger = logging.getLogger(log_file_name)
    logger.setLevel(logging.DEBUG)

    # Creating console handler.
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.DEBUG)

    # Creating formatter.
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:   %(message)s","%Y-%m-%d %H:%M:%S")
    console_logger.setFormatter(formatter)

    # Adding to logger.
    logger.addHandler(console_logger)

    return logger


def init_client(token):
    # Initialising and running client.
    client = discord.Client(intents=intents)

    # Initialising events.
    init_events(client)
    logger.info("Initialising events.")
    logger.info("Running client.")
    client.run(TOKEN,reconnect=True,log_handler=None)

    return client


def init_events(client):
    # On guild join event.
    @client.event
    async def on_guild_join(guild):
        logger.info(f"Joined discord server ({guild.name}).")

        # Creating "Workflow" category.
        main_category = await guild.create_category(name="Workflow")
        logger.info('Created category ("Workflow")')

        # Creating default channels.
        if "COMMUNITY" in guild.features:
            deadlines_channel = await guild.create_forum("Deadline",topic="Displaying all current deadlines.",position=0)
            stage_channel = await guild.create_stage_channel("Conclave", category=main_category,position=3)
        chat_channel = await guild.create_text_channel("Discussion",category=main_category,topic="Chat dedicated to general workflow discussion.",position=1)
        ideas_channel = await guild.create_text_channel("Ideas",category=main_category,topic="Chat dedicated to sharing potential ideas.",position=2)
        voice_channel = await guild.create_voice_channel("Meeting Room", category=main_category,position=4)
        logger.info("Default channels created.")
        
# - - - - - - - - - - - - - - - - - - - - - - - 

if __name__ == "__main__":
    # Initialising logging.
    init_logging()

    # Initialising intents.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    # Initialising client.
    client = init_client(TOKEN)



    