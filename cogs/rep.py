from ButtonMenu import ButtonMenu
import discord
import random
from discord import app_commands
from discord.utils import get
from discord.ext import commands
import datetime
from typing import Optional


class Rep(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="How about thank 'em for what they did 😼")
    @app_commands.describe(member="Member you want to thank", reason="why do you wanna thank them")
    async def thank(self,interaction:discord.Interaction,member:discord.Member,reason:Optional[str]="No reason specified"):

        if interaction.user==member:
            return await interaction.response.send_message(
                "You can't be thanking yourself, can you? :confused:", ephemeral=True
            )
        if member.bot:
            return await interaction.response.send_message(
                "Thanking a bot? please specify a **member**", ephemeral=True
            )

        await self.bot.check(member.id)
        await self.bot.add_rep(member.id)

        em = discord.Embed(
            title=f"Congratulations {member.name} :partying_face: ",
            description=f"You have been thanked by **{interaction.user.name}** with **+1** rep <a:rep:935432721352773652>\nReason: {reason}",
            color=random.choice(self.bot.colors),
        )
        await interaction.response.send_message(embed=em, content=member.mention)

    @app_commands.command(description="Have a look at yours/others rep")
    @app_commands.describe(member="Who's rep do you wanna see")
    async def reps(self,interaction:discord.Interaction,member:Optional[discord.Member]=None):
        name = member or interaction.user
        reps = await self.bot.db.fetchrow(
            "SELECT rep FROM users WHERE userid = $1", name.id
        )
        if not reps or not reps[0]:
            return await interaction.response.send_message(
                f"{name.name} has no reputation :(", ephemeral=True
            )

        reps = reps[0]
        if reps == 1:
            degree = "Newbie"
        elif reps >= 2 and reps < 5:
            degree = "Rookie"
        elif reps >= 5 and reps < 10:
            degree = "Intermediate"
        elif reps >= 10 and reps < 20:
            degree = "Proficient"
        elif reps >= 20 and reps < 50:
            degree = "Professional"
        else:
            degree = "**ULTIMATE**"

        em = discord.Embed(
            title="Reputation",
            description=f"Reputation of {name.name} is **{reps} rep(s)** <a:rep:935432721352773652>\nDegree: {degree}",
            color=random.choice(self.bot.colors),
        )
        em.timestamp = datetime.datetime.utcnow()
        await interaction.response.send_message(embed=em)

    @app_commands.command(description="Who's the most reputed? Check the leaderboard here")
    async def replb(self, interaction:discord.Interaction):
        lb = await self.bot.db.fetch("SELECT * FROM users ORDER BY rep DESC NULLS LAST")
        member_ids = [i.id for i in interaction.guild.members]
        lb = [i for i in lb if i[0] in member_ids]
        if len(lb)==0: return await interaction.response.send_message("No reputations of any user found in this guild :(", ephemeral=True)

        names = [
            f"**{i}.** {get(interaction.guild.members,id = j[0]).name.title()}"
            for i, j in enumerate(lb, 1)
            if j[4]
                ]
        

        reps = [f"**{i[4]}** <a:rep:935432721352773652>" for i in lb if i[4]]
        
        embeds = []
        loops= len(names)//5+1
        for x in range(loops):
            embed = discord.Embed(
                    title="Reputation leaderboard",
                    color=random.choice(self.bot.colors),
                    timestamp=datetime.datetime.utcnow(),
                )
            if x!=loops:
                nameset,repset="\n".join(names[5*x:5*x+5]),"\n".join(reps[5*x:5*x+5])
            else:
                nameset,repset="\n".join(names[5*x:]),"\n".join(reps[5*x:])

            embed.add_field(name="Name", value=nameset)
            embed.add_field(name="Reps", value=repset, inline=True)
            embeds.append(embed)

        if len(embeds)==1: await interaction.response.send_message(embed=embed)
        else: await interaction.response.send_message(embed=embeds[0],view=ButtonMenu(embeds,30,interaction, True))


async def setup(bot):
    await bot.add_cog(Rep(bot), guilds=[discord.Object(id=775940596279410718)])
