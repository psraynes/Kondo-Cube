import discord
import datetime
from discord.ext import tasks
import scrython as scry

local = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
time = datetime.time(hour=9, minute=00, tzinfo=local)

class MyClient(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sparks_joy_list = []
        self.does_not_spark_joy_list = []

        self.last_card_message_id = None
        self.channel_id = 1466458603010654319 # replace with your channel ID

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

        description = ''

        # Check reactions on last card message
        if self.last_card_message_id is not None:
            total_sparks_joy = 0
            total_does_not_spark_joy = 0
            try:
                last_message = await channel.fetch_message(self.last_card_message_id)
                for reaction in last_message.reactions:
                    if reaction.emoji == '💖':
                        total_sparks_joy += reaction.count - 1  # exclude bot's own reaction
                    elif reaction.emoji == '😭':
                        total_does_not_spark_joy += reaction.count - 1  # exclude bot's own reaction

                card_info = last_message.embeds[0].footer.text
                card_name, card_set, card_number = card_info.split(':')
                if total_sparks_joy > total_does_not_spark_joy:
                    description += f'The community has chosen: {card_name} ･｡･ﾟ✧ ＳＰＡＲＫＳ  ＪＯＹ ✧･ﾟ｡･ﾟ with {total_sparks_joy} votes! Added to the list.\n\n'
                    self.sparks_joy_list.append(card_info)
                elif total_does_not_spark_joy > total_sparks_joy:
                    description += f'The community has chosen: {card_name} Does Not Spark Joy with {total_does_not_spark_joy} votes! Added to the list.\n\n'
                    self.does_not_spark_joy_list.append(card_info)
                else:
                    description += f'The community is tied on {card_name} with {total_sparks_joy} Sparks Joy votes and {total_does_not_spark_joy} Does Not Spark Joy votes!\n\n'

            except discord.NotFound:
                pass  # message was deleted

        card = self.get_new_card()

        title = f'DOES {card.name} | {card.set_name}  ✨🌸･｡:★:｡･ﾟ✧･ﾟ･✧  ＳＰＡＲＫ  ＪＯＹ  ✧･ﾟ･✧･ﾟ｡:★:｡･ﾟ🌸✨?'
        description += f"React with 💖 if it  ✨🌺･｡:★:｡･ﾟ✧･ﾟ･✧  ＳＰＡＲＫ  ＪＯＹ  ✧･ﾟ･✧･ﾟ｡:★:｡･ﾟ🌺✨, React with 😭 if it doesn't."
        embed = discord.Embed(title=title, description=description)
        embed.set_image(url=card.image_uris['png'])
        embed.set_footer(text=f'{card.name}:{card.set}:{card.collector_number}')
        message = await channel.send(embed=embed)
        self.last_card_message_id = message.id
        await message.add_reaction('💖')
        await message.add_reaction('😭')

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    def get_new_card(self):
        # get filter to exclude current cards
        random_card = scry.cards.Random()
        return random_card

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!newsparksjoyordoesnotsparkjoy'):
            # Check reactions on last card message

            description = ''
            if self.last_card_message_id is not None:

                total_sparks_joy = 0
                total_does_not_spark_joy = 0
                try:
                    last_message = await message.channel.fetch_message(self.last_card_message_id)
                    for reaction in last_message.reactions:
                        if reaction.emoji == '💖':
                            total_sparks_joy += reaction.count - 1  # exclude bot's own reaction
                        elif reaction.emoji == '😭':
                            total_does_not_spark_joy += reaction.count - 1  # exclude bot's own reaction

                    card_info = last_message.embeds[0].footer.text
                    card_name, card_set, card_number = card_info.split(':')

                    if total_sparks_joy > total_does_not_spark_joy:
                        description += f'The community has chosen: {card_name} ･｡･ﾟ✧ ＳＰＡＲＫＳ  ＪＯＹ ✧･ﾟ｡･ﾟ with {total_sparks_joy} votes! Added to the list.\n\n'
                        self.sparks_joy_list.append(card_info)
                    elif total_does_not_spark_joy > total_sparks_joy:
                        description += f'The community has chosen: {card_name} Does Not Spark Joy with {total_does_not_spark_joy} votes! Added to the list.\n\n'
                        self.does_not_spark_joy_list.append(card_info)
                    else:
                        description += f'The community is tied on {card_name} with {total_sparks_joy} Sparks Joy votes and {total_does_not_spark_joy} Does Not Spark Joy votes!\n\n'

                except discord.NotFound:
                    pass  # message was deleted

            card = self.get_new_card()
            title = f'DOES {card.name} | {card.set_name}\n ✨🌸･｡:★:｡･ﾟ✧  ＳＰＡＲＫ  ＪＯＹ  ✧･ﾟ｡:★:｡･ﾟ🌸✨?'
            description += f"React with 💖 if it  ･｡･ﾟ✧ ＳＰＡＲＫＳ  ＪＯＹ ✧･ﾟ｡･ﾟ, React with 😭 if it doesn't."
            embed = discord.Embed(title=title, description=description)
            embed.set_image(url=card.image_uris['normal'])
            embed.set_footer(text=f'{card.name}:{card.set}:{card.collector_number}')
            new_message = await message.channel.send(embed=embed)
            self.last_card_message_id = new_message.id
            await new_message.add_reaction('💖')
            await new_message.add_reaction('😭')

        if message.content.startswith('!joylist'):
            sparks_list_str = '\n'.join(self.sparks_joy_list) if self.sparks_joy_list else 'No cards in Sparks Joy list yet.'
            await message.channel.send(f'✨🌸･｡:★:｡･ﾟ✧  ＳＰＡＲＫＳ  ＪＯＹ  ✧･ﾟ｡:★:｡･ﾟ🌸✨:\n{sparks_list_str}')

        if message.content.startswith('!nojoylist'):
            does_not_spark_list_str = '\n'.join(self.does_not_spark_joy_list) if self.does_not_spark_joy_list else 'No cards in Does Not Spark Joy list yet.' 
            await message.channel.send(f'Does Not Spark Joy:\n{does_not_spark_list_str}')

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run('YOUR_BOT_TOKEN_HERE')