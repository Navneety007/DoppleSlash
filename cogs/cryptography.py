import discord
import base64
import random
from discord import app_commands
from googletrans import Translator
from typing import Optional
from discord.ext import commands
from ButtonMenu import DM


SYMBOLS = ["@", "#", "$", "%", "=", ":", "?", ".", "/", "|", "~", ">", "*", "(", ")"]

class Cryptography(commands.Cog):
    """Commands and helps for securing data"""

    def __init__(self, bot):
        self.bot = bot

    encode = app_commands.Group(name="encode",description="Encode an image or a piece of text")
    decode = app_commands.Group(name="decode",description="Decode the encoded image or piece of text")

    @encode.command(description="Create an encoded text from your image *grins")
    @app_commands.describe(image="Paste or attach your image")
    async def image(self, interaction:discord.Interaction,image:discord.Attachment):
        image_url = f"{image.url}^^^{interaction.user.name}"
        ss = image_url.encode("ascii")
        base64_bytes = base64.b64encode(ss)
        base64_string = base64_bytes.decode("ascii")
        base64_string = base64_string.replace("==", "")
        embed = discord.Embed(title="Encoded image",
            description=f"```{base64_string}```Type `/decode image <this code>` to get the decoded image",
            color=0x36393F
        )
        await interaction.response.send_message(embed=embed)

    @encode.command(description="Encode a text message- totally not a confession")
    @app_commands.describe(message="Type your message")
    async def message(self, interaction:discord.Interaction, message: str):
        try:
            ss = message.encode("ascii")
            base64_bytes = base64.b64encode(ss)
            base64_string = base64_bytes.decode("ascii")
            embed = discord.Embed(title="Encoded message",
                                description=f"```{base64_string}```Type `/decode message <this code>` to get the decoded message",color=0x36393F)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Couldn't Encode the given string.",
                    color=discord.Colour.red(),
                ),
                ephemeral=True,
            )

    @decode.command(description="Time to decode your/their encoded image! hehe")
    @app_commands.describe(code="Paste the code of your encoded image")
    async def image(self, interaction:discord.Interaction, code: str):
        code = f"{code}=="
        try:
            base64_bytes = code.encode("ascii")
            sample_string_bytes = base64.b64decode(base64_bytes)
            sample_string = sample_string_bytes.decode("ascii")
            url, author = sample_string.split("^^^")
            embed = discord.Embed(title="Decoded image",color=0x36393F)
            embed.set_image(url=url)
            embed.set_footer(text=f"Image originally encoded by {author}")
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Couldn't decode the image :( make sure you didn't have a typo!",
                    color=discord.Colour.red(),
                ),
                ephemeral=True,
            )

    @decode.command(description="Reveal the encoded message")
    @app_commands.describe(code="Paste the code of your encoded message")
    async def message(self, interaction:discord.Interaction, code: str):
        try:
            base64_bytes = code.encode("ascii")
            sample_string_bytes = base64.b64decode(base64_bytes)
            sample_string = sample_string_bytes.decode("ascii")
            embed = discord.Embed(title="Decoded message", description=f"```{sample_string}```",color=0x36393F)
            embed.set_footer(text=f"type /encode message <your text> to encode your own message!")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Couldn't Decode the Code, make sure that you didn't have a typo",
                    color=discord.Colour.red(),
                ),
                ephemeral=True,
            )

    
    @app_commands.command(description="Translate any literal language! (Google Translator)")
    @app_commands.describe(text="Input the text")
    async def translate(self, interaction:discord.Interaction, text:str):
        trans = Translator()
        trs = trans.translate(text, dest="en")
        detected = trans.detect(text)
        embed = discord.Embed(color=random.choice(self.bot.colors))
        embed.set_author(
            name=f"Translation requested by {interaction.user.name}",
            icon_url=interaction.user.avatar.url,
        )
        embed.add_field(name="Original Message", value=f"`{text}`")
        embed.add_field(name="Translated Message", value=f"`{trs.text}`", inline=False)
        embed.set_footer(text=f"Translated from {detected.lang} to english")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Fed up of strong pswd required? Here's how you can make it strong")
    @app_commands.describe(keyword="Keyword as the base of your password", length="Minimum length of your password")
    async def password(self,interaction:discord.Interaction,keyword: str,length: Optional[app_commands.Range[int,1,30]]=8):
        if len(keyword)<=25:
            key, msg = keyword, "\t"
        else:
            key,msg = keyword[:25], "26 or subsequent characters in the key were skipped"
        cap_pass = "".join(random.choice((str.upper, str.lower))(c) for c in key)
        var1 = "".join(
            "%s%s" % (x, random.choice(("",random.choice(SYMBOLS), ""))) for x in cap_pass
        )
        var1 = "".join(
            "%s%s" % (x, random.choice(("",random.randrange(1,10),""))) for x in var1
        )
        try:
            var1 = var1.replace(" ", "")
        except:
            pass
        while len(var1) <= length:
            var1 += random.choice(SYMBOLS)

        embed = discord.Embed(
            description="Generated a new password stronger for you!",
            color=random.choice(self.bot.colors),
        )
        embed.add_field(name="Old Password", value=f"```{keyword}```"+msg, inline=False)
        embed.add_field(name="New Password", value=f"```{var1}```", inline=False)
        embed.add_field(name="Length", value=f"`{len(var1)}`")
        await interaction.response.send_message(embed=embed, ephemeral=True, view=DM(30, embed, interaction))

   


async def setup(bot):
    await bot.add_cog(Cryptography(bot), guilds = [discord.Object(id=775940596279410718)])
