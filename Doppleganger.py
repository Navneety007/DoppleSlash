from PIL import Image, ImageDraw, ImageFont, ImageChops
import discord
from discord import *
import asyncpg
import os
import json
from io import BytesIO
import random
from discord.ext import commands

colors = [
    0x0DD2FF,
    0x03F5FF,
    0x2AFFA9,
    0x18E6FF,
    0x17FFC2,
    0x03F5FF,
    0x30E79D,
]

os.environ['TOKEN']="ODQzMzU0ODE1ODMyNzg0OTA4.GQsTIG.KVcksVzdGrC7ykLLBntJfyjsdA4A40ttmnFxwg"

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_RETAIN", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")


def revert(time):
    if time <= 86000 and time > 3600:
        hrs = time // 3600
        mins = (time % 3600) / 60
        return f"{int(hrs)} hr(s) {int(mins)} min(s)"
    elif time <= 3600 and time > 60:
        times = time // 60
        secs = time % 60
        secs = str(secs)[:2]
        times = f"{int(times)} min(s) {secs} sec(s)"
        return times
    elif time <= 60:
        return f"Only {int(time)} sec(s) Left !"


def center(word):
    length = len(word)
    if length > 12:
        return f"{word[:11]}.."
    elif length == 12:
        return word
    else:
        spaces = int((12 - length) / 2)
        if spaces == 0:
            return f"{word} "
        else:
            return spaces * " " + word + spaces * " "


def circle(pfp, size):

    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")

    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


class Doppleganger(commands.Bot):
    def __init__(self, **options):
        super().__init__(
            command_prefix=f"!",
            help_command=None,
            description="Bot with amazing Economy, Profile, Guild, welcome etc. commands",
            case_insensitive=True,
            intents=discord.Intents.all(),
            owner_id=779743087572025354,
            application_id=843354815832784908,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
            **options,
        )

        self.colors = [
            0x0DD2FF,
            0x03F5FF,
            0x2AFFA9,
            0x18E6FF,
            0x17FFC2,
            0x03F5FF,
            0x30E79D,
        ]

        self.emotes = {
            "credits": "<a:credits:935420944653119499>",
            "rep": "<a:rep:935432721352773652>",
            "loading": "<a:loading:936309190740287548>",
            "tick": "<a:tick:819047828013056001>",
            "a": "<:a_card:938367907799384094>",
            "seven": "<:seven_card:938373121784836096>",
            "joker": "<:joker_card:938373122883723265>",
            "ten": "<:ten_card:938373121583484948>",
            "king": "<:king_card:938373121646411846>",
            "queen": "<:queen_card:938373121579319297>",
            "back" : "<:back_card:939202029212012554>"
        }

    # Economy, rep

    async def add(self, id, amount):
        money = await self.db.fetchrow(
            "SELECT credits FROM users WHERE userid = $1", id
        )
        await self.db.execute(
            "UPDATE users SET credits = $1 WHERE userid = $2", money[0] + amount, id
        )

    async def data(self, id):
        user = await self.db.fetchrow("SELECT * FROM users WHERE userid = $1", id)
        return user

    async def check(self, id):
        user = await self.db.fetch("SELECT * FROM users WHERE userid = $1", id)
        if not user:
            await self.db.execute(
                "INSERT INTO users (userid,credits,bg, crypto) VALUES ($1,$2,$3,$4)",
                id,
                2000,
                ["default"],
                []
            )

    async def add_rep(self, id):
        rep = await self.db.fetchrow("SELECT rep FROM users WHERE userid = $1", id)
        if not rep or not rep[0]:
            rep = 1
        else:
            rep = rep[0] + 213
        await self.db.execute("UPDATE users SET rep = $1 WHERE userid = $2", rep, id)

    async def additem(self, id, item):
        inventory = await self.db.fetchrow(
            "SELECT inventory FROM users WHERE userid = $1", id
        )
        if not inventory or not inventory[0]:
            inventory = []
        else:
            inventory = inventory[0]
        inventory.append(item)
        await self.db.execute(
            "UPDATE users SET inventory = $1 WHERE userid = $2", inventory, id
        )

    # Custom commands
    async def create_db_pool(self):
        self.db = await asyncpg.create_pool(
            database="Economy", user="postgres", password="12382692"
            )
        # self.db = await asyncpg.create_pool(os.environ['DATABASE_URL'],ssl = "require")

    async def base(self):
        async with bot:
            await bot.run(os.environ['TOKEN'])

    async def guild_check(self, guild: discord.Guild):
        guild_data = await self.db.fetchrow(
            "SELECT * FROM guild WHERE guildid = $1", guild.id
        )
        if not guild_data:
            return await self.db.execute(
                "INSERT INTO guild (guildid,template) VALUES ($1,$2)",
                guild.id,
                "gaming",
            )
        if not guild_data[4]:
            return await self.db.execute(
                "UPDATE guild SET template = $1 WHERE guildid = $2", "gaming", guild.id
            )

    async def onetime(self):
        await self.db.execute("ALTER TABLE guild DROP COLUMN prefix")
        await self.db.execute("ALTER TABLE guild DROP COLUMN aichannel")
        await self.db.execute("ALTER TABLE guild DROP COLUMN logchannel")
        await self.db.execute("ALTER TABLE guild RENAME COLUMN mainchannel TO welcome")
        await self.db.execute(
            "ALTER TABLE guild RENAME COLUMN suggestionchannel TO suggestion"
        )
        await self.db.execute("ALTER TABLE guild RENAME COLUMN logchannel TO logs")
        await self.db.execute("ALTER TABLE guild ADD COLUMN template TEXT")
        await self.db.execute("UPDATE guild SET template = $1", "gaming")
        await self.db.execute("ALTER TABLE users ADD COLUMN rep BIGINT")
        await self.db.execute("ALTER TABLE users ADD COLUMN streak BIGINT")
        await self.db.execute("ALTER TABLE users ADD COLUMN crypto JSONB")

    async def welcome_msg(self, member, background):
        background = Image.open(f"./Assets/images/{background}.png")
        draw = ImageDraw.Draw(background)

        asset = member.avatar.with_format("png")
        asset2 = member.guild.icon.with_format("png")
        data = BytesIO(await asset.read())
        data2 = BytesIO(await asset2.read())
        pfp = Image.open(data).convert("RGB")
        logo = Image.open(data2).convert("RGB")

        logo = circle(logo, (93, 93))
        pfp = circle(pfp, (308, 308))

        Lfont = ImageFont.FreeTypeFont("./Assets/fonts/DrumNBass-ywGy2.ttf", size=65)
        Mfont = ImageFont.FreeTypeFont("./Assets/fonts/Roboto-Black.ttf", size=27)
        Sfont = ImageFont.FreeTypeFont("./Assets/fonts/Roboto-Black.ttf", size=10)

        guild_name = (
            f"{member.guild.name[:20]}..."
            if len(member.guild.name) > 20
            else member.guild.name
        )
        member_name = f"{str(member)[:20]}.." if len(str(member)) > 20 else str(member)
        member_joined = member.created_at.strftime("%d %B, %Y")
        member_count = str(len([i for i in member.guild.members if not i.bot]))
        channel = "youtube.com/codestacks"
        info = f"{member_name}\n\nID: {member.id}\n\nAccount made: {member_joined}\n\nPosition: You are the {member_count}th member"

        draw.text(
            (490, 212),
            info,
            font=Mfont, 
            fill=(255, 255, 255),
            stroke_fill=(0, 0, 0),
            stroke_width=2,
        )
        draw.text((565, 124), center(guild_name), font=Lfont, fill=(255, 255, 255))
        draw.text((960, 492), channel, font=Sfont, fill=(255, 255, 255))
        background.paste(pfp, (102, 104), pfp)
        background.paste(logo, (1001, 16), logo)

        return background

    async def crypto(self,id:int):
        data = await self.db.fetchrow("SELECT crypto FROM users WHERE userid = $1",id)
        if data and data['crypto']:
            return json.loads(data['crypto'])
        else:
            await self.db.execute("UPDATE users SET crypto = $1 WHERE userid = $2",json.dumps({}),id)
            return dict()


    async def cryptoStack(self,id:int,data:dict):
        await self.db.execute("UPDATE users SET crypto = $1 WHERE userid = $2",json.dumps(data),id)

    # Default events

    async def setup_hook(self):
        #await self.loop.run_until_complete(await self.create_db_pool())
        for i in os.listdir("./cogs"):
            if i.endswith(".py"):
                await self.load_extension(f"cogs.{i[:-3]}")
        
        await bot.create_db_pool()
        await bot.tree.sync(guild = discord.Object(id=775940596279410718))


    async def on_ready(self):
        print(f"{self.user.name} bot loaded with {int(self.latency*100)} ping")
        # self.dispatch("member_join",get(self.get_all_members(),id = 813350886675841065))

    async def on_guild_join(self, guild):
        desc = f"Hi, I am **DoppleGanger** :wave:\nEnjoy noble economy/anime/crypto commands, image profile, welcome image, etc."
        embed = discord.Embed(
            description=f"{desc}\n```Start by /help to know my commands```",
            color=random.choice(colors),
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_footer(text="Join the main server for more features")
        for channel in guild.channels:
            if str(channel.type) == "text":
                if "general" in channel.name or "main" in channel.name:
                    await channel.send(embed=embed)
                    await self.db.execute(
                        "INSERT INTO guild (guildid,welcome,template) VALUES ($1,$2,$3)",
                        guild.id,
                        channel.id,
                        "gaming",
                    )
                    break
        else:
            for channel in guild.channels:
                if str(channel.type) == "text":
                    await channel.send(embed=embed)
                    await self.db.execute(
                        "INSERT INTO guild (guildid,welcome,template) VALUES ($1,$2,$3)",
                        guild.id,
                        channel.id,
                        "gaming",
                    )
                    break

    async def on_member_join(self, member):
        if member.bot:
            return
        guild_data = await self.db.fetchrow(
            "SELECT * FROM guild WHERE guildid = $1", member.guild.id
        )
        if not guild_data[1]:
            return

        background = await self.welcome_msg(member, guild_data[4])

        embed = discord.Embed(
            description=f"**{member.display_name}** Welcome to {member.guild.name.title()} \n Why not start with introducing yourself, and maybe get yourself some roles...",
            color=random.choice(colors),
        )
        embed.set_footer(text="Change the background theme by /welcomer templates")
        welcome_channel = discord.utils.get(member.guild.channels, id=guild_data[1])

        with BytesIO() as a:
            background.save(a, "PNG")
            a.seek(0)
            embed.set_image(url="attachment://profile.png")
            await welcome_channel.send(
                content=member.mention,
                file=discord.File(a, filename="profile.png"),
                embed=embed,
            )

    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond(
                embed=discord.Embed(
                    description="You do not have the required Permissions to Use this command\nContact the Admin/Mods for the following",
                    color=0xE74C3C,
                ),
                ephemeral=True,
            )

        elif isinstance(error, commands.errors.NotOwner):
            em = discord.Embed(
                title="You Do Not own this Bot!! ",
                description=f"Ask the Bot Owner for More info - {str(self.bot.get_user(self.bot.owner_id))}",
                color=0xE74C3C,
            )
            await ctx.send(embed=em, delete_after=8)

        elif isinstance(error, commands.CommandOnCooldown):
            msg = revert(error.retry_after)
            embed = discord.Embed(
                title="Cooldown", description=str(msg), color=16580705
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            embed.set_thumbnail(
                url="https://cdn.pixabay.com/photo/2012/04/13/00/22/red-31226_640.png"
            )
            await ctx.respond(embed=embed, delete_after=5, ephemeral=True)
        else:
            embed = Embed(
                title="Error",
                description="Oopsie, an unexpected error has occured, my dev is notified",
                color=Color.red(),
            )
            raise error

bot = Doppleganger()
#asyncio.run(bot.base())
bot.run(os.environ['TOKEN'])