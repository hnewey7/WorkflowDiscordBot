import discord

def run_discord_bot():
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running.')

    client.run(TOKEN)