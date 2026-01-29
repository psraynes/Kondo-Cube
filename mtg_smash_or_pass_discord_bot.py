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

        self.smash_list = []
        self.pass_list = []

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
            total_smash = 0
            total_pass = 0
            try:
                last_message = await channel.fetch_message(self.last_card_message_id)
                for reaction in last_message.reactions:
                    if reaction.emoji == '❤️':
                        total_smash += reaction.count - 1  # exclude bot's own reaction
                    elif reaction.emoji == '🤮':
                        total_pass += reaction.count - 1  # exclude bot's own reaction

                card_info = last_message.embeds[0].footer.text
                card_name, card_set, card_number = card_info.split(':')
                if total_smash > total_pass:
                    description += f'The community has chosen to Smash {card_name} with {total_smash} votes! Added to the Smash list.\n\n'
                    self.smash_list.append(card_info)
                elif total_pass > total_smash:
                    description += f'The community has chosen to Pass {card_name} with {total_pass} votes! Added to the Pass list.\n\n'
                    self.pass_list.append(card_info)
                else:
                    description += f'The community is tied on {card_name} with {total_smash} Smash votes and {total_pass} Pass votes!\n\n'

            except discord.NotFound:
                pass  # message was deleted

        card = self.get_new_card()

        title = f'SMASH OR PASS: {card.name} | {card.set_name}'
        description += f'React with ❤️ to add to Smash, React with 🤮 to add to Pass.'
        embed = discord.Embed(title=title, description=description)
        embed.set_image(url=card.image_uris['png'])
        embed.set_footer(text=f'{card.name}:{card.set}:{card.collector_number}')
        message = await channel.send(embed=embed)
        self.last_card_message_id = message.id
        await message.add_reaction('❤️')
        await message.add_reaction('🤮')

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

        if message.content.startswith('!newsmashorpass'):
            # Check reactions on last card message

            description = ''
            if self.last_card_message_id is not None:

                total_smash = 0
                total_pass = 0
                try:
                    last_message = await message.channel.fetch_message(self.last_card_message_id)
                    for reaction in last_message.reactions:
                        if reaction.emoji == '❤️':
                            total_smash += reaction.count - 1  # exclude bot's own reaction
                        elif reaction.emoji == '🤮':
                            total_pass += reaction.count - 1  # exclude bot's own reaction

                    card_info = last_message.embeds[0].footer.text
                    card_name, card_set, card_number = card_info.split(':')

                    if total_smash > total_pass:
                        description += f'The community has chosen to Smash {card_name} with {total_smash} votes! Added to the Smash list.\n\n'
                        self.smash_list.append(card_info)
                    elif total_pass > total_smash:
                        description += f'The community has chosen to Pass {card_name} with {total_pass} votes! Added to the Pass list.\n\n'
                        self.pass_list.append(card_info)
                    else:
                        description += f'The community is tied on {card_name} with {total_smash} Smash votes and {total_pass} Pass votes!\n\n'

                except discord.NotFound:
                    pass  # message was deleted

            card = self.get_new_card()
            title = f'SMASH OR PASS: {card.name} | {card.set_name}'
            description += f'React with ❤️ to add to Smash, React with 🤮 to add to Pass.'
            embed = discord.Embed(title=title, description=description)
            embed.set_image(url=card.image_uris['normal'])
            embed.set_footer(text=f'{card.name}:{card.set}:{card.collector_number}')
            new_message = await message.channel.send(embed=embed)
            self.last_card_message_id = new_message.id
            await new_message.add_reaction('❤️')
            await new_message.add_reaction('🤮')

        if message.content.startswith('!smashlist'):
            smash_list_str = '\n'.join(self.smash_list) if self.smash_list else 'No cards in Smash list yet.'
            await message.channel.send(f'Smash List:\n{smash_list_str}')

        if message.content.startswith('!passlist'):
            pass_list_str = '\n'.join(self.pass_list) if self.pass_list else 'No cards in Pass list yet.' 
            await message.channel.send(f'Pass List:\n{pass_list_str}')

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run('YOUR_DISCORD_BOT_TOKEN_HERE')