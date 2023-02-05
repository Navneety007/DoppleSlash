from discord import ButtonStyle, app_commands
from discord.ext import commands
from discord.app_commands import Choice
from discord.ui import View, button
import discord
import random
from io import BytesIO
import asyncio
from typing import Literal, Optional
from better_profanity import profanity

sugs = {}


template_dict = {
    "Anime": "https://i.imgur.com/Y9OpWXj.png",
    "Abstract": "https://i.imgur.com/RNutQbx.png",
    "Future": "https://i.imgur.com/HiH9LIU.png",
    "Gaming": "https://i.imgur.com/LOkZQPJ.png",
}

class sugView(View):
    def __init__(self, timeout: float, interaction:discord.Interaction,message:discord.Embed):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.embed = message
        
        print(sugs)

    @button(emoji="👍",style=ButtonStyle.green)
    async def favour(self,interaction,button):
        sugs[self.interaction.user.id][interaction.user.id] = True
        await interaction.response.send_message("Your response has been added in favour 👍",ephemeral = True)

    @button(emoji="👎",style = ButtonStyle.blurple)
    async def against(self,interaction,button):
        sugs[self.interaction.user.id][interaction.user.id] = False
        await interaction.response.send_message("Your response has been added in opposition 👎",ephemeral = True)

    @button(label = "End",style=ButtonStyle.red,custom_id="endhe")
    async def end(self,interaction,button):
        if interaction.user.id == self.interaction.user.id:
            favour,opp = len([i for i in list(sugs[self.interaction.user.id].values()) if i]),len([i for i in list(sugs[self.interaction.user.id].values()) if i==False])
            
            self.embed.title,self.embed.description = "Poll results for:", self.embed.description+"\n[Ended in between by the author]"
            self.embed.add_field(name="Favour",value=favour)
            self.embed.add_field(name="Opposition",value=opp)
            if favour>opp: result = "Result: In favour"; self.embed.color = discord.Color.green()
            elif favour<opp: result = "Result: In against"; self.embed.color = discord.Color.red()
            elif favour==opp: result = "Result: Tie breaker"; self.embed.color = discord.Color.dark_grey()
            self.embed.set_footer(text=result)
            for i in self.children:
                i.disabled=True
            await self.interaction.edit_original_message(embed = self.embed,view = self)
            del sugs[interaction.user.id]
            self.stop()
        else:
            return await interaction.response.send_message("This suggestion was not sent by you -_-",ephemeral = True)


    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id in list(sugs[self.interaction.user.id].keys()) and interaction.user.id != self.interaction.user.id and interaction.data['custom_id']!="endhe":
            await interaction.response.send_message("You've already responded to this suggestion before.....",ephemeral=True)
            return False
        return True
    
    

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    welcome = app_commands.Group(name="welcome", description="Commands in relevance with welcomer")
    set = app_commands.Group(name="set", description="Commands for setting up the Utility channels")

    @app_commands.command(description="Poll on a suggestion")    
    @app_commands.describe(suggestion="Type your suggestion",duration="Default duration: 24 hrs")
    @app_commands.choices(duration = [
        Choice(name="1 min",value=60),
        Choice(name="5 mins",value=300),
        Choice(name="30 mins",value=1800),
        Choice(name="1 hr",value=3600),
        Choice(name="6 hrs",value=21600),
        Choice(name="12 hrs",value=43200),
        Choice(name="1 day",value=86400),
    ])
    async def suggest(self,interaction:discord.Interaction,suggestion:str,duration:Optional[int]=86400):

        sug = await self.bot.db.fetchrow("SELECT suggestion FROM guild WHERE guildid = $1",interaction.guild_id)
        if not sug or not sug[0]:
            embed = discord.Embed(title="Suggestion channel not set", description="Ask any moderator/admin to set suggestion channel to enjoy this command.\nType `/set suggestion` to specify a channel for suggestions",color = discord.Color.red())
            return await interaction.response.send_message(embed = embed)
        sugChannel = discord.utils.get(interaction.guild.channels,id = sug[0])
        
        if interaction.user.id in list(sugs.keys()):
            return await interaction.response.send_message(f"You already have an on going suggestion in <#{sugChannel.id}>\nPlease end it before starting a new one",ephemeral=True)
        if interaction.channel!=sugChannel:
            return await interaction.response.send_message(f"Please use <#{sugChannel.id}> for sending suggestions, this channel is not appropriate for the same",ephemeral=True)


        sugs[interaction.user.id] = {}
        sugEmbed = discord.Embed(title = "Suggestion poll",description=f"`{profanity.censor(suggestion)}`",color = interaction.user.color)
        sugEmbed.set_footer(text="Type /suggest to send your own suggestion")
        sugEmbed.set_author(name = f"By {interaction.user.name}",icon_url=interaction.user.display_avatar.url)
        sview = sugView(duration,interaction,sugEmbed)
        await interaction.response.send_message(embed = sugEmbed,view = sview)
        await asyncio.sleep(duration)
        if interaction.user.id not in list(sugs.keys()): return
        sugEmbed.title = "Poll results for:"
        favour,opp = len([i for i in list(sugs[interaction.user.id].values()) if i]),len([i for i in list(sugs[interaction.user.id].values()) if i==False])
        sugEmbed.add_field(name="Favour",value=favour)
        sugEmbed.add_field(name="Opposition",value=opp)
        if favour>opp: result = "Result: In favour"; sugEmbed.color = discord.Color.green()
        elif favour<opp: result = "Result: In against"; sugEmbed.color = discord.Color.red()
        elif favour==opp: result = "Result: Tie breaker"; sugEmbed.color = discord.Color.dark_grey()
        sugEmbed.set_footer(text=result)
        for i in sview.children:
            i.disabled=True
        await interaction.edit_original_message(embed = sugEmbed,view = sview)
        sview.stop()
        del sugs[interaction.user.id]


    @welcome.command(description="View the available templates")
    async def templates(self, interaction:discord.Interaction):
        ref = str()
        counter=1
        for name, link in template_dict.items():
            ref+=f"{counter}) **{name.title()}**: [View]({link})\n"
            counter+=1
        
        
        embed = discord.Embed(
            title="Available templates",
            description=f"Type `/welcome update [template name]` to set one of the templates \nand `/welcome test [template name]` to test any template\n\n{ref}",
            color=random.choice(self.bot.colors),
        )
        await interaction.response.send_message(embed=embed)

    @welcome.command(description="Test any template for welcoming")
    @app_commands.describe(template="Templates to try out")
    async def test(self,interaction:discord.Interaction,template: Optional[Literal[tuple(template_dict.keys())]]=None):
        if not template:
            template = await self.bot.db.fetchrow("SELECT template FROM guild WHERE guildid=$1",interaction.guild_id)
            template = template[0]
            if not template: 
                template = "gaming"
            await self.bot.db.execute(
                "UPDATE guild SET template = $1 WHERE guildid= $2",
                template,
                interaction.guild_id,
            )

        await interaction.response.defer()
        image = await self.bot.welcome_msg(interaction.user, template.lower())

        with BytesIO() as a:
            image.save(a, "PNG")
            a.seek(0)
            await interaction.followup.send(
                file=discord.File(a, filename="profile.png")
            )

    @welcome.command(description="Update any particular template")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def update(self,interaction:discord.Interaction,template: Literal[tuple(template_dict.keys())]):

        await self.bot.guild_check(interaction.guild)
        await self.bot.db.execute(
            "UPDATE guild SET template = $1 WHERE guildid= $2",
            template,
            interaction.guild_id,
        )
        embed = discord.Embed(
            description=f"**Welcome template** Updated to `{template.title()}` by {interaction.user.name}",
            color=random.choice(self.bot.colors),
        )
        embed.set_image(url=template_dict[template])
        embed.set_footer(text="Type /welcome test [template name] to see how it looks")
        return await interaction.response.send_message(embed=embed)

    @set.command(description="Set up channel for suggestions")
    @app_commands.checks.has_permissions(manage_channels = True)
    @app_commands.describe(channel="Channel to be set for suggestions command")
    async def suggestion(self,interaction:discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()
        embed = discord.Embed(
            title="Suggestion channel updated",
            description=f"Suggestion channel has been set to {channel.mention} by {interaction.user.mention}\nYou can type `/suggest` to send your suggestion and poll on it",
            color=random.choice(self.bot.colors),
        )
        embed.set_footer(
            text="Contact Mod/Admin(s) if you feel the channel is not appropriate for this purpose"
        )
        embed.set_thumbnail(
            url="https://www.pngall.com/wp-content/uploads/4/Settings-PNG-Images.png"
        )
        try:
            test = await channel.send(
                f"Setting up {channel.name} for suggestions <a:loading:936309190740287548> [Step:1/2]"
            )
            await asyncio.sleep(0.5)
            await test.edit(content=f"Checking for required permissions <a:loading:936309190740287548> [Step:2/2]")
            await asyncio.sleep(0.5)
            await test.edit(content="Success! <a:tick:819047828013056001>",delete_after=2)

        except Exception as e:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Failed ❌",
                    description=f"Bot doesn't have the required permissions to send messages in {channel.mention}\nPlease grant with the same",
                    color=discord.Color.red(),
                )
            )
        await self.bot.db.execute(
            "UPDATE guild SET suggestion = $1 WHERE guildid = $2",
            channel.id,
            interaction.guild_id,
        )
        await interaction.followup.send(embed=embed)
   
    @set.command(description="Set up channel for welcome message")
    @app_commands.checks.has_permissions(manage_channels = True)
    @app_commands.describe(channel="Channel for sending welcome message")
    async def welcome(self, interaction:discord.Interaction, channel: discord.TextChannel):
        
        await interaction.response.defer()
        embed = discord.Embed(
            title="Welcome channel updated",
            description=f"Welcome channel has been set to {channel.mention}\nType `/welcome update` or `/welcome test` to set or test any template",
            color=random.choice(self.bot.colors),
        )
        embed.set_footer(
            text="Contact any Mod/Admin if you feel the channel is not appropriate for welcoming"
        )
        embed.set_thumbnail(
            url="https://www.pngall.com/wp-content/uploads/4/Settings-PNG-Images.png"
        )
        try:
            test = await channel.send(
                content=f"Setting up {channel.name} for welcome images <a:loading:936309190740287548> [Step:1/2]"
            )
            await asyncio.sleep(0.5)
            await test.edit(
                content=f"Checking for required permissions <a:loading:936309190740287548> [Step:2/2]"
            )
            await asyncio.sleep(0.5)
            await test.edit(content="Success! <a:tick:819047828013056001>", delete_after=2)
        except:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Failed",
                    description=f"Bot doesn't have the required permissions to send messages in {channel.mention}\nPlease grant with the same",
                    color=discord.Color.red(),
                )
            )
        await self.bot.db.execute(
            "UPDATE guild SET welcome = $1 WHERE guildid = $2", channel.id, interaction.guild_id
        )
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot), guilds = [discord.Object(id=775940596279410718)])
