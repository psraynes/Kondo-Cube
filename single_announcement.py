import discord
import datetime
from discord.ext import tasks
import scrython as scry
from scrython.base import ScrythonRequestHandler
import requests as req
from PIL import Image
from io import BytesIO
import json

with open('config.json') as f:
    config = json.load(f)

local = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
time = datetime.time(hour=config['hour'], minute=config['minute'], tzinfo=local)
print(time)
print(datetime.datetime.now(local))
ScrythonRequestHandler.set_user_agent('MTG Sparks Joy Bot v1.0')

class MyClient(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sparks_joy_file = 'sparks_joy_list.txt'
        self.does_not_spark_joy_file = 'does_not_spark_joy_list.txt'

        self.last_card_message_id = None
        self.channel_id = int(config['channel_id'])
        self.guild_id = int(config['guild_id'])

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(time=time)  # task runs every day at 9:00 local time
    async def my_background_task(self):
        channel = self.get_channel(self.channel_id)  # channel ID goes here
        # Tell the type checker that this is a messageable channel
        assert isinstance(channel, discord.abc.Messageable)

        message = 'Hi, Im Magic Tinder Bot. I will be posting a card every day for you to vote on whether or not it ✨🌸･｡:★:｡･ﾟ✧･ﾟ･✧  ＳＰＡＲＫＳ  ＪＯＹ  ✧･ﾟ･✧･ﾟ｡:★:｡･ﾟ🌸✨.\n' \
        'To vote, simply react to the card with a 💖 if it sparks joy, or a 😭 if it does not spark joy. I will keep track of the votes and update the lists accordingly!\n' \
        'You can check the current lists with the following commands: \n**!joylist** for the list of cards that ･｡･ﾟ✧ ＳＰＡＲＫ  ＪＯＹ ✧･ﾟ｡･ﾟ \n**!nojoylist** for the list of cards that do not'

        await channel.send(message)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run(config['bot_token'])