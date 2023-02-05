import asyncio
import wonderwords, re
from discord.ui import View, Modal, TextInput
import discord
from discord import app_commands
import random
from discord.ext import commands
from typing import Optional
import traceback

roasts = [
    "I'd give you a nasty look but you've already got one",
    "If you were going to be two-faced at least make one of them pretty",
    "I love what you've done with your hair. How do you get it to come out of the nostrils like that",
    "If laughter is the best medicine your face must be curing the world",
    "The only way you'll ever get laid is if you crawl up a chicken's ass and wait",
    "It looks like your face caught fire and someone tried to put it out with a hammer",
    "I'd like to see things from your point of view... but I can't seem to get my head that far up your ass",
    "I've seen people like you before but I had to pay admission",
    "Scientists say the universe is made up of neutrons protons and electrons. They forgot to mention morons",
    "You're so fat you could sell shade",
    "Your lips keep moving but all I hear is Blah blah blah",
    "Your family tree must be a cactus because everyone on it is a prick",
    "You'll never be the man your mother is",
    "I'm sorry was I meant to be offended? The only thing offending me is your face",
    "Someday you'll go far... and I hope you stay there",
    "Which sexual position produces the ugliest children? Ask your mother",
    "Stupidity's not a crime so you're free to go",
    "If I had a face like yours I'd sue my parents",
    "Your doctor called with your colonoscopy results. Good news - they found your head",
    "No those pants don't make you look fatter - how could they",
    "Save your breath - you'll need it to blow up your date",
    "You're not stupid you just have bad luck when thinking",
    "If you really want to know about mistakes you should ask your parents",
    "Please keep talking. I always yawn when I am interested",
    "The zoo called. They're wondering how you got out of your cage",
    "Whatever kind of look you were going for you missed",
    "I was hoping for a battle of wits but you appear to be unarmed",
    "Aww it's so cute when you try to talk about things you don't understand",
    "I don't know what makes you so stupid but it really works",
    "You are proof that evolution can go in reverse",
    "Brains aren't everything. In your case they're nothing",
    "I thought of you today It reminded me to take the garbage out",
    "You're so ugly when you look in the mirror your reflection looks away",
    "I'm sorry I didn't get that - I don't speak idiot",
    "Quick - check your face! I just found your nose in my business",
    "It's better to let someone think you're stupid than open your mouth and prove it",
    "Hey your village called - they want their idiot back",
    "Were you born this stupid or did you take lessons",
    "I've been called worse by better",
    "You're such a beautiful intelligent wonderful person. Oh I'm sorry I thought we were having a lying competition",
    "I may love to shop but I'm not buying your bull",
    "I'd slap you but I don't want to make your face look any better",
    "Calling you an idiot would be an insult to all stupid people",
    "I just stepped in something that was smarter than you... and smelled better too",
    "You have the right to remain silent because whatever you say will probably be stupid anyway",
    "Your so ugly Hello Kitty said goodbye to you",
    "Could you take a couple steps back. I'm allergic to idiots",
    "Your so big a picture of you would fall off the wall",
    "You look like a before picture",
    "You know that feeling when you step in gum... that's how i feel looking at you",
    "You couldn't find logic if it hit you in the face",
    "My phone battery lasts longer than your relationships",
    "Oh you’re talking to me. I thought you only talked behind my back",
    "Too bad you can’t count jumping to conclusions and running your mouth as exercise",
    "If I wanted a bitch I would have bought a dog",
    "My business is my business. Unless you’re a thong... get out of my ass",
    "It’s a shame you can’t Photoshop your personality",
    "Jealousy is a disease. Get well soon",
    "When karma comes back to punch you in the face... I want to be there in case it needs help",
    "You have more faces than Mount Rushmore",
    "Maybe you should eat make-up so you’ll be pretty on the inside too",
    "Whoever told you to be yourself gave you really bad advice",
    "I thought I had the flu... but then I realized your face makes me sick to my stomach",
    "You should try the condom challenge. If your gonna act like a dick then dress like one too",
    "I’m jealous of people who don’t know you",
    "You sound reasonable… Time to up my medication",
    "Please say anything. It’s so cute when you try to talk about things you don’t understand",
    "I suggest you do a little soul searching. You might just find one",
    "You should try this new brand of chap stick. The brand is Elmer's",
    "I'd smack you if it wasn't animal abuse",
    "Why is it acceptable for you to be an idiot but not for me to point it out",
    "If you’re offended by my opinion... you should hear the ones I keep to myself",
    "If you’re going to be a smart ass... first you have to be smart. Otherwise you’re just an ass",
    "I’m not an astronomer but I am pretty sure the earth revolves around the sun and not you",
    "Keep rolling your eyes. Maybe you’ll find your brain back there",
    "No no no. I am listening. It just takes me a minute to process that much stupidity",
    "Sorry... what language are you speaking. Sounds like Bullshit",
    "Everyone brings happiness to a room. I do when I enter... you do when you leave",
    "You’re the reason I prefer animals to people",
    "You’re not stupid; you just have bad luck when thinking",
    "Please... keep talking. I always yawn when I am interested",
    "Were you born this stupid or did you take lessons?",
    "You have the right to remain silent because whatever you say will probably be stupid anyway",
    "Hey you have something on your chin… no… the 3rd one down",
    "You’re impossible to underestimate",
    "You’re kinda like Rapunzel except instead of letting down your hair... you let down everyone in your life",
    "You look like your father would be disappointed in you if he stayed",
    "You look like you were bought on the clearance shelf",
    "Take my lowest priority and put yourself beneath it",
    "You are a pizza burn on the roof of the world’s mouth",
    "People like you are the reason God doesn’t talk to us anymore",
    "You’re so dense that light bends around you",
    "I don’t have the time or the crayons to explain anything to you",
    "You’re not as dumb as you look. That's saying something",
    "You’ve got a great body. Too bad there’s no workout routine for a face",
    "You’re about as important as a white crayon",
    "I fear no man. But your face... it scares me",
    "We get straight to the point. We aren't Willy Wonka",
]

class Party(View):
    def __init__(self, timeout:int, emoji, event:str, user, host, interaction:discord.Interaction):
        super().__init__(timeout=timeout)
        self.emoji = emoji
        self.event = event
        self.user = user
        self.host = host
        self.interaction = interaction
        self.children[0].emoji = self.emoji

    @discord.ui.button(label="Join in", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction, button):
        self.clear_items()
        await interaction.response.edit_message(
            embed=discord.Embed(
                description=f"{self.host.name} and {interaction.user.name} are enjoying {self.event} {self.emoji} Together!",
                color=discord.Color.green(),
            ),
            view=None,
        )
        self.stop()

    async def on_timeout(self):
        await self.interaction.edit_original_message(
            embed=discord.Embed(
                description=f"Looks like {self.user.mention} is busy.",
                color=discord.Color.red(),
            ), view=None
        )

    
    async def interaction_check(self, interaction) -> bool:
        if interaction.user == self.host:
            await interaction.response.send_message(
                "You placed the offer at the first place- -_- ; Please wait for the person to accept.",
                ephemeral=True)
            return False
        if interaction.user != self.user:
            await interaction.response.send_message(
                "This Offer is for someone else T^T",
                ephemeral=True,
            )
            return False
        return True



class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  


    @app_commands.command(description="Want to roast a fella?")
    @app_commands.describe(member="Name the target")
    async def roast(self, interaction:discord.Interaction, member: discord.Member):
        if member == interaction.user:
            return await interaction.response.send_message("You can't be roasting yourself :smile:", ephemeral=True)
        roast = random.choice(roasts)

        await interaction.response.send_message(f"{member.name} {roast}")

    @app_commands.command(description="How about killing someone *evil grin")
    @app_commands.describe(member="Name the target")
    async def kill(self, interaction:discord.Interaction, member: discord.Member):

        if member == interaction.user:
            return await interaction.response.send_message(
                "You can't be killing yourself :confused:", ephemeral=True
            )

        killing = [
            "{} was shot by {} using Axe",
            "{} walked into a cactus whilst trying to escape {}",
            "{} drowned whilst trying to escape {}",
            "{} was fireballed by {} using Catapult",
            "{} was killed by {} using ShotGun",
            "{} walked into fire whilst fighting {}",
            "{} tried to swim in lava to escape {}",
            "{} walked on danger zone due to {}",
            "{} was burnt to a crisp whilst fighting {}",
            "{} was slain by {} using Axe",
            "{} was pummeled by {}",
            "{} experienced kinetic energy whilst trying to escape {}",
            "{} was blown up by {} with bazooka!",
            "{} was squashed by a falling anvil plotted by {} ",
            "{} was doomed to fall by {}",
            "{} skewered by a falling stalactite of {}"
            "{} was lead to fall by {} using Log",
            "{} tried to swim in lava to escape {} and tut"
            "{} fell too far and was finished by {}",
            "{} was obliterated by a sonically-charged shriek of {}",
            "{} didn't want to live in the same world as {} lmfao"
        ]

        await interaction.response.send_message(random.choice(killing).format(member.name,interaction.user.name))


    @app_commands.command(description="Potion to bring dead chats alive ^-^")
    async def topic(self, interaction:discord.Interaction):
        file = open("./Assets/text/questions.txt", "r", encoding="utf8")
        topics = [i for i in file]
        random.shuffle(topics)
        topic = random.choice(topics)
        embed = discord.Embed(description=topic, color=random.choice(self.bot.colors))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="How about a cup of coffee or with someone")
    @app_commands.describe(member="Person you wanna enjoy coffee with")
    async def coffee(self,interaction:discord.Interaction,member:Optional[discord.Member]=None):
        
        if member == interaction.user or not member:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"☕ | {interaction.user.name} Enjoying Coffee alone :relieved: ",
                    color=random.choice(self.bot.colors),
                )
            )

        elif str(member) == "Doppelganger#0726":
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description="☕ | and Here I enjoy coffee with ya  *sips*",
                    color=random.choice(self.bot.colors),
                )
            )

        elif member.bot:
            return await interaction.response.send_message(
                "Other bots aren't pro like me to drink coffee with ya :smirk:",
                ephemeral=True
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"{member.mention}, you got a coffee ☕ offer from {interaction.user.name}",
                color=random.choice(self.bot.colors),
            ),
            view=Party(30, "☕", "Coffee", member, interaction.user, interaction),
        )

    @app_commands.command(description="Glass of beer to enjoy alone or with someone")
    @app_commands.describe(member="Person you wanna drink beer with")
    async def beer(self,interaction:discord.Interaction,member:Optional[discord.Member]=None):
        if member == interaction.user or not member:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"🍺 | {interaction.user.name} Party Time !! , *Enjoying Beer*",
                    color=random.choice(self.bot.colors),
                )
            )

        elif str(member) == "Doppelganger#0726":
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description="🍺 | Don't worry I will Enjoy beer with you  *slurps*",
                    color=random.choice(self.bot.colors),
                )
            )

        elif member.bot:
            return await interaction.response.send_message(
                "Bots couldn't get any noob, demn you can't enjoy beer with 'em, *'cept me*",
                ephemeral=True
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"{member.mention}, you got a Beer 🍺 offer from {interaction.user.name}",
                color=random.choice(self.bot.colors),
            ),
            view=Party(30,"🍺","Beer",member,interaction.user,interaction),
        )


async def setup(bot) -> None:
    await bot.add_cog(Fun(bot),guilds=[discord.Object(id=775940596279410718)])
