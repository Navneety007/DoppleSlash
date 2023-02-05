from code import interact
from typing import Literal, Optional
import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ui import View
import yfinance
import datetime
import matplotlib.pyplot as plot
import random
import io

cryptos = {'bitcoin':'BTC-USD',
'ethereum' :'ETH-USD',
'tether' :'USDT-USD',
'tron' :'TRX-USD',
'dai' :'DAI-USD',
'avalanche':'AVAX-USD',
'cardano' :'ADA-USD',
'xrp' :'XRP-USD',
'binance' :'BNB-USD',
'solana' :'SOL-USD',
'dogecoin' :'DOGE-USD',
'hex' :'HEX-USD',
'polkadot':'DOT-USD',
}
cryptocache = []

class Offer(View):
    def __init__(self, timeout: float, interaction:discord.Interaction,offer:int,embed:discord.Embed,desc:str):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.ans = None
        self.embed = embed
        self.offer = offer
        self.desc = desc
        cryptocache.append(self.interaction.user.id)

    @discord.ui.button(label="Sale off",emoji="💰",style=discord.ButtonStyle.green)
    async def accept(self,interaction,button):
        self.ans = True
        for i in self.children:
            i.disabled = True
        self.embed.description, self.embed.color = self.desc, 0x2ecc71
        for i in range(4): self.embed.remove_field(0)
        await interaction.response.edit_message(view=self,embed=self.embed)
        cryptocache.remove(self.interaction.user.id)
        self.stop()
    
    @discord.ui.button(label="Cancel",style=discord.ButtonStyle.red)
    async def decline(self,interaction,button):
        self.ans = False
        for i in self.children:
            i.disabled = True
        self.embed.description, self.embed.color = "Declined for `{:,}` credits".format(self.offer), 0xe74c3c
        for i in range(4): self.embed.remove_field(0)
        await interaction.response.edit_message(view=self,embed=self.embed)
        cryptocache.remove(self.interaction.user.id)
        self.stop()

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.interaction.user:
            await interaction.followup.send(
                "This offer is for someone else\nType `/sell` to sell your own item(s)",
                ephemeral=True,
            )
            return False
        else: return True

    
    async def on_timeout(self):
        self.ans = False
        self.embed.description, self.embed.color = f"Timeout!\nDeclined for {self.offer} credits", 0xe74c3c
        for i in range(4): self.embed.remove_field(0)
        for i in self.children:
            i.disabled = True
        cryptocache.remove(self.interaction.user.id)
        await self.interaction.edit_original_message(view=self,embed=self.embed)



class CryptoCurrency(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    crypto = app_commands.Group(name="crypto",description="Crypto currency simulator")

    @crypto.command(description="Statistics of any particular crypto currency")
    @app_commands.describe(crypto="Choose the crypto you want to check",duration="Time period for crypto statistics")
    @app_commands.choices(duration = [
        Choice(name="3 months", value="3mo"),
        Choice(name="6 months", value="6mo"),
        Choice(name="1 year",value="1y"),
        Choice(name="Last month", value="1mo"),
        Choice(name="Lifetime",value="max")

    ])
    async def stats(self,interaction:discord.Interaction,crypto:Literal[tuple([i.title() for i in list(cryptos.keys())])],duration:Optional[str]="6mo"):
        await interaction.response.defer()
        id = interaction.user.id
        await self.bot.check(id)
        crypto = crypto.lower()
        Ucrypto = await self.bot.crypto(id)
        cryptoData = yfinance.Ticker(cryptos[crypto])
        stats = cryptoData.history(period=duration)
        embeds = []

        if crypto in list(Ucrypto.keys()):
            invested,date,ratio = Ucrypto[crypto][0],Ucrypto[crypto][1],Ucrypto[crypto][2]
            userEmbed = discord.Embed(title="Your Stats",description=f"Last invested/traded on `{datetime.datetime.fromtimestamp(date).strftime('%d %b %Y')}`",color = interaction.user.color)
            
            currentVal = float("{:.2f}".format(stats['Close'][-1]*ratio))
            percent = float("{:.2f}".format(float(((currentVal-invested)/invested)*100)))
            emote = "🟢" if percent>0 else "🔴"
            display = "`{:,}` (**{}%** {})".format(currentVal,percent,emote)
            
            userEmbed.add_field(name="Investment",value="`{:,}` {}".format(invested,self.bot.emotes['credits']))
            userEmbed.add_field(name="Current value",value=display)
            userEmbed.set_footer(text="Type /crypto sell to redeem their values")
            embeds.append(userEmbed)


        embed = discord.Embed(title=f"{cryptoData.info['name']} ({cryptoData.info['symbol']})",description=f"{cryptoData.info['description'][:100]}...\nNote: Do not make **investments** in real time on the basis on bot simulation of crypto market", color = random.choice(self.bot.colors))
        
        embed.add_field(name="Volume",value="`{:,}`".format(cryptoData.info['volume']),inline=True)
        embed.add_field(name="Market cap",value="`{:,}`".format(cryptoData.info['marketCap']),inline=True)
        embed.set_footer(text="Type /crypto invest to start trading in simulator")

        
        stats['Close'].plot()
        ax = plot.gca()
        plot.xlabel('Time')
        plot.ylabel('Credits (1 credit = 1 USD)')
        ax.legend(['Close'])
        plot.title(label=cryptoData.info['name'])
        with io.BytesIO() as buf:
            plot.savefig(buf, format='PNG',bbox_inches="tight")
            buf.seek(0)
            embed.set_image(url="attachment://crypto.png")
            embeds.insert(0,embed)
            await interaction.followup.send(file = discord.File(buf, filename = "crypto.png"), embeds = embeds)
            plot.clf()
        

    @crypto.command(description="How about making some monehhh by trading?")
    @app_commands.describe(crypto="Select the crypto",amount = "Credits you want to invest/trade")
    async def invest(self,interaction:discord.Interaction,crypto:Literal[tuple([i.title() for i in list(cryptos.keys())])],amount:app_commands.Range[int,100,1000000]):
        id = interaction.user.id
        await self.bot.check(id)
        crypto = crypto.lower()
        data = await self.bot.data(id)
        balance = data['credits']
        Ucrypto = await self.bot.crypto(id)

        cryptoData = yfinance.Ticker(cryptos[crypto])
        stats = cryptoData.history(period="1m")

        embeds = []
        
        if crypto in list(Ucrypto.keys()):
            Pinvested,date,ratio = Ucrypto[crypto][0],Ucrypto[crypto][1],Ucrypto[crypto][2]
            soldAt =int(ratio*stats['Close'][-1])
            percent = float("{:.2f}".format(float(((soldAt-Pinvested)/Pinvested)*100)))
            emote = "🟢" if percent>0 else "🔴"
            embed = discord.Embed(title="Crypto traded",description=f"Your previous investments made into {crypto.title()} on `{datetime.datetime.fromtimestamp(date).strftime('%d %b %Y')}` were traded",color=random.choice(self.bot.colors))
            embed.add_field(name="Invested",value="`{:,}` {}".format(Pinvested,self.bot.emotes['credits']))
            embed.add_field(name="Sold value",value="`{:,}` {}".format(soldAt,self.bot.emotes['credits']),inline=True)
            embed.add_field(name="Gain/Loss %",value="**{}%** {}".format(percent,emote))
            embed.set_footer(text="Credits were successfully added into your account!")
            await self.bot.add(id,soldAt)
            del Ucrypto[crypto]
            await self.bot.cryptoStack(id,Ucrypto)
            data = await self.bot.data(id)
            balance = data['credits']
            Ucrypto = await self.bot.crypto(id)
            embeds.append(embed)

        if balance<amount: return await interaction.response.send_message(f"You do not have enough credits to invest `{amount}` in crypto\nType /help to seek ways to earn credits",ephemeral=True)
        
        time = datetime.datetime.now().timestamp()
        ratio = amount/stats['Close'][-1]
        Ucrypto[crypto] = [amount,time,ratio]
        await self.bot.add(id,-amount)
        await self.bot.cryptoStack(id,Ucrypto)
        
        embed2 = discord.Embed(title = "Traded",description="{} successfully invested `{:,}` {} credits in {}\nType `/crypto stats` to keep a track on your investments".format(interaction.user.name,amount,self.bot.emotes['credits'], crypto.title()),color = random.choice(self.bot.colors))
        embeds.append(embed2)
        await interaction.response.send_message(embeds = embeds)

    @crypto.command(description="Redeem your crypto values")
    async def sell(self,interaction:discord.Interaction,crypto:Literal[tuple([i.title() for i in list(cryptos.keys())])] ):
        id = interaction.user.id
        if id in cryptocache:return await interaction.response.send_message("Please complete the previous sale to start a new one",ephemeral=True)

        await self.bot.check(id)
        crypto = crypto.lower()
        Ucrypto = await self.bot.crypto(id)
        if crypto not in list(Ucrypto.keys()): return await interaction.response.send_message(f"You don't own any {crypto.title()} cryptos at the moment\nType `/crypto invest` to start investing in {crypto.title()}",ephemeral=True)
        
        cryptoData = yfinance.Ticker(cryptos[crypto])
        stats = cryptoData.history(period="1m")

        embed = discord.Embed(title = "Trading crypto",description="Are you sure about making this transaction?",color = random.choice(self.bot.colors))
        Pinvested,date,ratio = Ucrypto[crypto][0],Ucrypto[crypto][1],Ucrypto[crypto][2]
        current =int(ratio*stats['Close'][-1])
        percent = float("{:.2f}".format(float(((current-Pinvested)/Pinvested)*100)))
        emote = "🟢" if percent>0 else "🔴"
        embed.add_field(name="Original investment",value="`{:,}` {}".format(Pinvested,self.bot.emotes['credits']))
        embed.add_field(name="Current value",value="`{:,}` {}".format(current,self.bot.emotes['credits']))
        embed.add_field(name="Gain/Loss %",value="`{}%` {}".format(percent,emote),inline=False)
        embed.set_footer(text="Profits/losses might magnify over the time")
        dealview = Offer(20,interaction,current,embed,f"Successfully sold {crypto.title()} with net **{percent}%** {emote} profit/loss")
        await interaction.response.send_message(embed= embed,view = dealview)
        result = await dealview.wait()
        if not result:
            if dealview.ans==True:
                await self.bot.add(id,current)
                del Ucrypto[crypto]
                await self.bot.cryptoStack(id,Ucrypto)
    



        





    
        





async def setup(bot):
    await bot.add_cog(CryptoCurrency(bot),guilds = [discord.Object(id = 775940596279410718)])