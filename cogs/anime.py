import animec
import discord
import datetime
from discord.ui import View
import random
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from ButtonMenu import DM 
from typing import Optional,Literal



class Anime(commands.Cog):
    """Anime commmands for weebs"""
    def __init__(self,bot: commands.Bot) -> None:
        self.bot=bot

    anime = app_commands.Group(name="anime", description="Anime commands")

    @anime.command(description="Search literally any anime for info regarding rating, episodes, status...")
    @app_commands.describe(name="Enter the anime name")
    async def search(self, interaction:discord.Interaction, name: str):
        await interaction.response.defer()
        try:
            anime = animec.Anime(name)
        except:
            return await interaction.followup.send(
                embed=discord.Embed(
                    description="No corresponding Anime is found for the search query",
                    color=discord.Color.red(),
                ),delete_after=5
            )

        embed = discord.Embed(
            title=anime.title_english,
            url=anime.url,
            description=f"{anime.description[:200]}...",
            color=random.choice(self.bot.colors),
        )
        embed.add_field(name="Episodes", value=str(anime.episodes))
        embed.add_field(name="Rating", value=str(anime.rating))
        embed.add_field(name="Broadcast", value=str(anime.broadcast))
        embed.add_field(name="Status", value=str(anime.status))
        embed.add_field(name="Type", value=str(anime.type))
        embed.add_field(name="NSFW status", value=str(anime.is_nsfw()))
        embed.set_thumbnail(url=anime.poster)
        await interaction.followup.send(embed=embed)

    @anime.command(description="Search any anime Character")
    @app_commands.describe(name="Enter the character name")
    async def character(self, interaction:discord.Interaction, name: str):
        await interaction.response.defer()
        try:
            char = animec.Charsearch(name)
        except:
            return await interaction.followup.send(
                embed=discord.Embed(
                    description="No corresponding Anime Character is found for the search query",
                    color=discord.Color.red(),
                ),
                delete_after=6,
            )

        embed = discord.Embed(
            title=char.title, url=char.url, color=random.choice(self.bot.colors)
        )
        embed.set_image(url=char.image_url)
        embed.set_footer(text=", ".join(list(char.references.keys())[:2]))
        await interaction.followup.send(embed=embed)

    @anime.command(description="Get the fresh latest news regarding Anime industry")
    @app_commands.describe(amount="Count of news [Default: 3]")
    async def news(self,interaction:discord.Interaction,amount: Optional[app_commands.Range[int,1,6]]=3):

        await interaction.response.defer()

        news = animec.Aninews(amount)
        links = news.links
        titles = news.titles
        descriptions = news.description

        embed = discord.Embed(
            title="Latest Anime News",
            color=random.choice(self.bot.colors),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_thumbnail(url=news.images[0])

        for i in range(amount):
            embed.add_field(
                name=f"{i+1}) {titles[i]}",
                value=f"{descriptions[i][:200]}...\n[Read more]({links[i]})",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @anime.command(description="Getting bored? Enjoy waifus privately")
    @app_commands.describe(type="Select the Waifu type [Default: waifu]")
    async def waifu(self,interaction:discord.Interaction,type: Optional[Literal["bite",
                "blush",
                "cry",
                "cuddle",
                "dance",
                "handhold",
                "happy",
                "highfive",
                "hug",
                "kick",
                "kiss",
                "lick",
                "pat",
                "poke",
                "random",
                "shinobu",
                "slap",
                "smile",
                "smug",
                "waifu",
                "wink",
                "yeet"]]="waifu"):

        await interaction.response.defer(ephemeral = True)
        waifu = getattr(animec.Waifu, type)
        waifu = waifu()
        embed=discord.Embed(color=random.choice(self.bot.colors))
        embed.set_image(url=waifu)
        await interaction.followup.send(embed=embed, view=DM(30,embed, interaction))

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Anime(bot),guilds=[discord.Object(id=775940596279410718)])