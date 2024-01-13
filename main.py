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
    log_file_name = "logs\\" + start_time + ".log"
    
    # Creating logger.
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Creating console handler.
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)

    # Creating file handler.
    file_logger = logging.FileHandler(log_file_name)
    file_logger.setLevel(logging.INFO)

    # Creating formatter.
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:   %(message)s","%Y-%m-%d %H:%M:%S")
    file_logger.setFormatter(formatter)
    console_logger.setFormatter(formatter)

    # Adding to logger.
    logger.addHandler(file_logger)
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

        # Creating "Workflow Manager" role.
        await guild.create_role("Workflow Manager", color=discord.Color.teal, reason="Role for editting the workflow.")
        logger.info("Workflow Manager role has been created.")
        
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



    