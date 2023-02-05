from async_timeout import asyncio
from discord import app_commands
import discord
from discord.ui import View,Button
import random
import datetime
from typing import Literal, Optional
from discord.ext import commands
from ButtonMenu import ButtonMenu
import uuid

gambleButtonIds = {}
member_cache = {}
trades = []

empty = "‎"

animals = [
    "hamster",
    "rabbit",
    "fox",
    "bear",
    "chicken",
    "mouse",
    "pig",
    "koala",
    "wolf",
    "boar",
]
fishes = [
    "whale",
    "blowfish",
    "lobster",
    "octopus",
    "squid",
    "dolphin",
    "shark",
    "seal",
]
dig = [
    "soccer",
    "boomerang",
    "badminton",
    "lacrosse",
    "dart",
    "jigsaw",
    "violin",
    "pill",
    "key"
]

collectables = {"crown":5000,"trophy":1199,"rosette":919,"volcano":2299,"syringe":699, "dolls":599}

names = [
    "Jenny",
    "Lauren",
    "Humble",
    "Dan",
    "Matthew",
    "Blacksmith",
    "Clarke",
    "Simon",
    "Christian",
    "Hector",
    "Albert",
    "Vader",
    "Walker",
    "Phillip",
]

class Offer(View):
    def __init__(self, timeout: float, interaction:discord.Interaction,offer:int,embed:discord.Embed,desc:str):
        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.ans = None
        self.embed = embed
        self.offer = offer
        self.desc = desc
        trades.append(self.interaction.user.id)

    @discord.ui.button(label="Accept",emoji="💰",style=discord.ButtonStyle.green)
    async def accept(self,interaction,button):
        self.ans = True
        for i in self.children:
            i.disabled = True
        self.embed.description, self.embed.color = self.desc, 0x2ecc71
        await interaction.response.edit_message(view=self,embed=self.embed)
        trades.remove(self.interaction.user.id)
        self.stop()
    
    @discord.ui.button(label="Decline",style=discord.ButtonStyle.red)
    async def decline(self,interaction,button):
        self.ans = False
        for i in self.children:
            i.disabled = True
        self.embed.description, self.embed.color = f"Declined for **{self.offer}** credits", 0xe74c3c
        await interaction.response.edit_message(view=self,embed=self.embed)
        trades.remove(self.interaction.user.id)
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
        for i in self.children:
            i.disabled = True
        trades.remove(self.interaction.user.id)
        await self.interaction.edit_original_message(view=self,embed=self.embed)

class MemorizeButton(Button):
    def __init__(self,x,y):
        self.id = str((x*5)+y-1)
        super().__init__(label=empty, style=discord.ButtonStyle.grey, custom_id=self.id, row=x)
        
    async def callback(self, interaction):
        await self.view.check(self.id,self,interaction)

class Memorize(View):
    def __init__(self, timeout:int, member:discord.Member=None, answer=None, bot=None, interaction:discord.Interaction=None):
        super().__init__(timeout=timeout)
        for x in range(0,4):
            for y in range(1,6):
                self.add_item(MemorizeButton(x,y))

        if not answer:
            self.answer = random.sample(range(0, 19), 7)
            for i in self.answer:
                self.children[i].style = discord.ButtonStyle.blurple
                for i in self.children:
                    i.disabled = True
                member_cache[member.id] = self.answer
                self.stop()
        else:
            self.start = datetime.datetime.utcnow()
            self.answer = answer
            for i in self.answer:
                self.children[i].style = discord.ButtonStyle.gray
        self.bot = bot
        self.member = member
        self.interaction = interaction

    async def on_timeout(self):
        credits = 40
        embed = discord.Embed(
            title="Oopsie",
            description=f"{self.member.mention} didn't answer in time\nYou earned **{credits} credits** <a:credits:935420944653119499> for working partway",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow(),
        )
        for i in self.children:
            i.disabled = True
        return await self.interaction.followup.send(embed=embed)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.member:
            await interaction.followup.send(
                "This work command is for someone else\nType `/work` to start your own",
                ephemeral=True,
            )
            return False
        else: return True

    async def check(self, custom_id, button:discord.Button, interaction:discord.Interaction):
        if int(custom_id) in self.answer:
            button.style = discord.ButtonStyle.green
            button.disabled = True
            self.answer.remove(int(custom_id))
            await interaction.response.edit_message(content="GG", view=self)
            if len(self.answer) == 0:
                for i in self.children:
                    i.disabled = True
                time = str(datetime.datetime.utcnow() - self.start)
                time = time[:-5][5:]
                if time[0] == "0":
                    time = time[1:]
                time = float(time)
                credits = int((((30 - time) * 30) / ((30 - time) + 30)) * 50)
                embed = discord.Embed(
                    description=f"{interaction.user.mention} completed it in **{time}** seconds\nYou earned **{credits} credits** <a:credits:935420944653119499> through `/work`",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.utcnow(),
                )
            else:
                return
        else:
            if len(self.answer) == 0:
                return
            button.style = discord.ButtonStyle.red
            button.disabled = True
            for i in self.answer:
                self.children[i].style = discord.ButtonStyle.blurple
            await interaction.response.edit_message(
                content="You answered wrong!", view=self
            )
            credits = (8 - len(self.answer)) * 30
            embed = discord.Embed(
                description=f"**Oopsie**\n{interaction.user.mention} didn't answer correctly\nYou earned **{credits} credits** <a:credits:935420944653119499> for working partway",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow(),
            )

        await self.bot.add(interaction.user.id, credits)
        await interaction.followup.send(embed=embed)
        self.stop()

class gambleCards(Button):
    def __init__(self,id,back,bot,member):
        super().__init__(style = discord.ButtonStyle.grey, emoji = back, custom_id=id)
        self.id = id
        for i,j in gambleButtonIds[member.id].items():
            if j==id:
                self.emote = bot.emotes[i]
                self.name = i

    async def callback(self, interaction):
        self.view.card = self.id
        self.emoji = self.emote
        eliminate = ""
        if self.name in self.view.userdeck:
            eliminate = f"You eliminated {self.emote} card from your deck\n[Pair matched]"
        else:
            eliminate = f"No pair matched"
        await interaction.response.edit_message(embed = discord.Embed(description=f"You got {self.emote} from Bot's deck\n{eliminate}",color = discord.Color.green()),view = self.view)
        self.view.stop()

class Gamble(View):
    def __init__(self,botdeck,userdeck,bot,member,timeout = 180):
        super().__init__(timeout=timeout)
        self.card = None
        self.member = member
        self.userdeck = userdeck
        IDs = {}
        for i in botdeck:
            IDs[i] = str(uuid.uuid4())
        gambleButtonIds[member.id] = IDs
        for i in botdeck:
            self.add_item(gambleCards(IDs[i],bot.emotes['back'],bot,member))

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.member:
            await interaction.response.send_message(
                "This gamble command is for someone else\nType `/gamble` to start your own",
                ephemeral=True,
            )
            return False
        else: return True


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wrongformat = discord.Embed(title="Wrong format!",description="Please address the following to sell any of your items",color=random.choice(self.bot.colors))
        self.wrongformat.add_field(name = "Sell a particular item",value="/sell [fishes/...] item_name item_count[Optional]\nEx:- `/sell animals hamster` (this will sell all of the hamsters)\nOr `/sell animals hamster 1`")
        self.wrongformat.add_field(name = "Sell all items",value="/sell [fishes/animals/collectables/items] all\nEx:- `/sell fishes all`")
        self.wrongformat.set_footer(text="Join the official server to gain instant 10k credits")
        
    def cards(self):
        cards = ["a","seven","ten","king","queen"]
        random.shuffle(cards)
        userDeck,botDeck = [],[]
        userIs = bool(random.randrange(1,2000)%2)
        if userIs: 
            userDeck.append("joker")
            for i in cards[:4]: userDeck.append(i)
            random.shuffle(cards)
            for i in cards:botDeck.append(i)
        else:
            botDeck.append("joker")
            for i in cards[:4]: botDeck.append(i)
            random.shuffle(cards)
            for i in cards:userDeck.append(i)

        return userDeck,botDeck

    def getList(self,ratio:float):
        final = []
        for i in range(int((1-ratio)*1000)):
            final.append(random.choice(dig))
        for j in range(int(ratio*1000)):
            final.insert(random.randrange(len(final)+1),random.choice([*collectables.keys()]))
        return final

    @app_commands.command(description="Check yours/others credits balance")
    async def balance(self,interaction:discord.Interaction,member:Optional[discord.Member]=None):
        member = member or interaction.user
        if member.bot: return await interaction.response.send_message(content="Other bots ain't pro enough to enjoy my economy commands :smirk:",ephemeral=True)
        await self.bot.check(member.id)
        data = await self.bot.data(member.id)
        balance = data[1]

        embed = discord.Embed(description=f"Balance: `{balance}` {self.bot.emotes['credits']}\nType `/leaderboard` to check the global/local leaderboard",color = member.color)
        embed.set_author(name = str(member),icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Join the official server to gain instant 10k credits")
        await interaction.response.send_message(embed = embed)


    @app_commands.command(description="Dig in, who knows you might encover relics?")
    @app_commands.describe(invest="The more credits you invest, more is probability of getting worthy items")
    async def dig(self, interaction:discord.Interaction, invest:app_commands.Range[int,50,500]):

        id = interaction.user.id
        await self.bot.check(id)
        data = await self.bot.data(id)
        balance = data[1]
        if invest>balance: 
            return await interaction.response.send_message(f"You don't have `{invest}` credits {self.bot.emotes['credits']} in your balance",ephemeral = True)
        await self.bot.add(interaction.user.id,-invest)
        item = random.choice(self.getList(invest/1000))
        if not item in collectables.keys():
            embed = discord.Embed(
                    description=f"Good going {interaction.user.name}\nYou found **{item.title()}** :{item}:"
                )
        else:
            embed = discord.Embed(
                description=f"WOOOW sugoi! {interaction.user.name}\nYou just found **{item.title()}** :{item}: collectable!"
            )
        await self.bot.additem(id, item)

        embed.title, embed.color = "Digging results", random.choice(self.bot.colors)
        embed.set_thumbnail(
            url="https://freepngimg.com/thumb/shovel/63772-moroni-shovel-angel-digging-dirt-free-download-png-hd.png"
        )
        embed.set_footer(text="Type /inventory to check your items")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Hunt down animals for the holy sake of credits!")
    async def hunt(self, interaction:discord.Interaction):

        id = interaction.user.id
        await self.bot.check(id)
        animal = random.choice(animals)
        result = random.randint(1, 4)
        if result != 3:
            embed = discord.Embed(
                description=f"Nice play {interaction.user.name}\nYou hunted down a **{animal.title()}** :{animal}:"
            )
            await self.bot.additem(id, animal)
            embed.set_thumbnail(
                url="https://images-ext-1.discordapp.net/external/I-NrhOHr73CNy5aYNPTascYP35V8gR7c1zXx2kcuGYA/https/assets.stickpng.com/images/5b4481ccc051e602a568ccd6.png"
            )

        else:
            embed = discord.Embed(
                description="Ah Better do a bit more Practice\nYou found nothing :x:"
            )
            embed.set_thumbnail(
                url="https://assets.stickpng.com/images/5b4481f3c051e602a568ccdb.png"
            )

        embed.title, embed.color = "Hunting results", random.choice(self.bot.colors)
        embed.set_footer(text="Type /inventory to check your items")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Catch fishes to sell them for credits")
    async def fish(self, interaction:discord.Interaction):

        id = interaction.user.id
        await self.bot.check(id)
        fish = random.choice(fishes)
        result = random.randint(1, 4)
        if result != 3:
            embed = discord.Embed(
                description=f"Well done {interaction.user.name}\nYou captured a **{fish.title()}** :{fish}:"
            )
            await self.bot.additem(id, fish)
            embed.set_thumbnail(
                url="https://assets.stickpng.com/images/58a1f1cac8dd3432c6fa81e7.png"
            )
        else:
            embed = discord.Embed(
                description=f"Better have more patience\nYou found nothing :confused:"
            )
            embed.set_thumbnail(
                url="https://assets.stickpng.com/images/58a1f1b1c8dd3432c6fa81e5.png"
            )

        embed.title, embed.color = "Fishing results", random.choice(self.bot.colors)
        embed.set_footer(text="Type /inventory to check your inventory")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Earn credits just by Memorizing")
    async def work(self, interaction:discord.Interaction):

        id = interaction.user.id
        await self.bot.check(id)
        view = Memorize(30, member=interaction.user, bot=self.bot)
        await interaction.response.send_message("Memorize it (2 seconds)", view=view)
        await asyncio.sleep(2)
        new_view = Memorize(
            30,
            answer=member_cache[interaction.user.id],
            member=interaction.user,
            bot=self.bot,
            interaction=interaction,
        )
        await interaction.edit_original_message(
            content="Fill the boxes which were earlier displayed", view=new_view
        )
        del member_cache[interaction.user.id]

    @app_commands.command(description="How about a round of Old maid?")
    @app_commands.describe(amount="Amount to bet")
    async def gamble(self, interaction:discord.Interaction,amount:app_commands.Range[int,200,5000]):
      
        id = interaction.user.id
        await self.bot.check(id)
        data = await self.bot.data(id)
        balance = data[1]
        if amount>balance: 
            return await interaction.response.send_message(f"You don't have `{amount}` credits {self.bot.emotes['credits']} in your balance",ephemeral = True)
      
        instructions = discord.Embed(description = f"Instructions:\n• You and the bot will get 5 cards each\n• One of the cards will be Joker\n• Pick one card from others deck and eliminate the matching card\n• The one left with **Joker** card at last will **loose** the game\n\nAmount gambled: `{amount}` {self.bot.emotes['credits']}",color = random.choice(self.bot.colors))
        instructions.set_author(url = "https://youtu.be/n6UFbZ0jGWw",name = "Old Maid",icon_url="https://image.winudf.com/v2/image1/anAuY28ucHJvamFwYW4ub2xkbWFpZF9pY29uXzE1NjcwNzIxOTBfMDIy/icon.png?fakeurl=1&h=240&type=webp")
        userDeck, botDeck = self.cards()

        async def btnCallback(interaction):
            await interaction.response.edit_message(view=None)
            timeout = discord.Embed(title = "Timeout!",description=f"You didn't respond in time :sad:\nYou lost `{amount}` credits {self.bot.emotes['credits']}",color = discord.Color.red())
            timeout.set_footer(text = "Type /gamble to play Old maid")
            desc = ""
            while len(userDeck)>0 and len(botDeck)>0:
                if len(botDeck)==1 and len(userDeck)==1: break
                embed = discord.Embed(title = "Your turn",description = "{}\nYour cards: {}".format(desc," ".join([self.bot.emotes[i] for i in userDeck])),color = random.choice(self.bot.colors))
                embed.add_field(name="Your cards",value = len(userDeck))
                embed.add_field(name="Bot's cards",value = len(botDeck))
                embed.set_footer(text="Choose one card from bot's Deck")
                gameview = Gamble(botDeck,userDeck,self.bot,interaction.user,timeout = 20)
                await interaction.followup.send(embed = embed,view = gameview)
                res = await gameview.wait()
                if res:
                    await interaction.followup.send(embed = timeout)
                    return await self.bot.add(interaction.user.id,-amount)
                    
                #User pick
                card = "".join([key for key,value in gambleButtonIds[interaction.user.id].items() if value == gameview.card])
                botDeck.remove(card)
                if card in userDeck: userDeck.remove(card)
                else: userDeck.append(card)
                del gambleButtonIds[interaction.user.id]
                if len(userDeck)==0:break
                #Bot pick
                if len(botDeck)==0: return
                random.shuffle(userDeck)
                pickcard = random.choice(userDeck)
                desc = f"Bot picked {self.bot.emotes[pickcard]} card from your deck"
                userDeck.remove(pickcard)
                if pickcard in botDeck: botDeck.remove(pickcard)
                else: botDeck.append(pickcard)
              
              
            win = False
            if "joker" in botDeck:
                win = True
            result = discord.Embed(title = "empty",color = discord.Color.red())
            result.set_footer(text="Type /gamble to play old maid")
            if win:
                result.title,result.description,result.color =f"Congratulations {interaction.user.name}",f"You won `{amount}` credits {self.bot.emotes['credits']} by gambling in Old maid \nas the bot ended up with Joker",discord.Color.green()
                await self.bot.add(interaction.user.id,amount)
            else:
                result.title,result.description = f"Oopsie {interaction.user.name}",f"You lose `{amount}` credits {self.bot.emotes['credits']} by as you ended up with Joker"
                await self.bot.add(interaction.user.id,-amount)
            return await interaction.followup.send(embed = result)
        rulesView = View()
        button = Button(label="Start Game",style = discord.ButtonStyle.green)
        rulesView.add_item(button)
        button.callback = btnCallback
        await interaction.response.send_message(embed = instructions,view = rulesView)

    #SELL commands

    sell = app_commands.Group(name="sell", description="Commands for selling your items")

    @sell.command(description="Sale off your fish(es)")
    @app_commands.describe(name="Fish name followed by amount with space, ex 'shark 2' or 'all'")
    async def fishes(self,interaction:discord.Interaction,name:str):
        id = interaction.user.id
        if id in trades:
            return await interaction.response.send_message("Please complete the previous trade to start a new one",ephemeral=True)
        await self.bot.check(id)
        data = await self.bot.data(id)
        inventory = data[2]
        finv = [i for i in inventory if i in fishes]
        buyer = random.choice(names)

        fish = name.lower().strip()
        if len(finv)==0: return await interaction.response.send_message("You don't have anything in your fish inventory :(\nType /fish to start catching fishes and earn credits",ephemeral=True)
    
        if fish == "all":
            offer = len(finv)*random.randrange(30,40)
            items = finv
            embed = discord.Embed(description = f"{buyer} is offering you **{offer}** {self.bot.emotes['credits']} for **All** [x{len(finv)}]  of your fish(es)",color = random.choice(self.bot.colors))
            desc = f"Sold all fishes for **{offer}** {self.bot.emotes['credits']}"
        else:
            fishvar = fish.split()
            name = fishvar[0]
            if name not in fishes:
                return await interaction.response.send_message(f"No fish named `{name}`, make sure you didn't have a typo",ephemeral=True)
            elif name not in finv: 
                return await interaction.response.send_message(f"You don't have **{name.title()}** :{name}: in your inventory\nType /fish to start catching fishes",ephemeral=True)
            
            if len(fishvar)>1:
                try:    
                    count = int(fishvar[1])
                except:
                    if fishvar[1]=="all":
                        count = len([i for i in finv if i==name])
                    else: return await interaction.response.send_message(embed=self.wrongformat)
            else: count = len([i for i in finv if i==name])

            if count>len([i for i in finv if i==name]):
                return await interaction.response.send_message(f"You don't have `{count}` no. of {name} :{name}: in your inventory\nType /fish to catch more",ephemeral=True)
            
            offer = count*random.randrange(30,40)
            items = [name for i in range(count)]
            embed = discord.Embed(description = f"{buyer} is offering you **{offer}** {self.bot.emotes['credits']} for {count} x {name.title()} :{name}:",color = random.choice(self.bot.colors))
            desc = f"Sold {count} x {name.title()} :{name}: for **{offer}** {self.bot.emotes['credits']}"
        embed.set_footer(text = "Rates of items keep fluctuating")
        embed.set_author(name = f"Offer for {interaction.user.name}",icon_url=interaction.user.display_avatar.url)
        offerview = Offer(30,interaction,offer,embed,desc)
        await interaction.response.send_message(embed=embed,view=offerview)
        result = await offerview.wait()
        if not result:
            if offerview.ans==True:
                await self.bot.add(id,offer)
                for i in items:
                    inventory.remove(i)
                await self.bot.db.execute("UPDATE users SET inventory = $1 WHERE userid = $2",inventory,id)
    
    
    @sell.command(description="Sale off your animal(s)")
    @app_commands.describe(name="Animal name followed by amount with space, ex 'hamster 1' or 'all'")
    async def animals(self,interaction:discord.Interaction,name:str):
        id = interaction.user.id
        if id in trades:
            return await interaction.response.send_message("Please complete the previous trade to start a new one",ephemeral=True)
        await self.bot.check(id)
        data = await self.bot.data(id)
        inventory = data[2]
        ainv = [i for i in inventory if i in animals]
        buyer = random.choice(names)

        animal = name.lower().strip()
        if len(ainv)==0: return await interaction.response.send_message("You don't have anything in your animal inventory :(\nType /hunt to start hunting animals and earn credits",ephemeral=True)
    
        if animal == "all":
            offer = len(ainv)*random.randrange(32,42)
            items = ainv
            embed = discord.Embed(description = f"{buyer} is offering you **{offer}** {self.bot.emotes['credits']} for **All** [x{len(ainv)}]  of your animal(s)",color = random.choice(self.bot.colors))
            desc = f"Sold all animals for **{offer}** {self.bot.emotes['credits']}"
        else:
            animalvar = animal.split()
            name = animalvar[0]
            if name not in animals:
                return await interaction.response.send_message(f"No animal named `{name}`, make sure you didn't have a typo",ephemeral=True)
            elif name not in ainv: 
                return await interaction.response.send_message(f"You don't have **{name.title()}** :{name}: in your inventory\nType /hunt to start hunting animals",ephemeral=True)
            
            if len(animalvar)>1:
                try:    
                    count = int(animalvar[1])
                except:
                    if animalvar[1]=="all":
                        count = len([i for i in ainv if i==name])
                    else: return await interaction.response.send_message(embed=self.wrongformat)
            else: count = len([i for i in ainv if i==name])

            if count>len([i for i in ainv if i==name]):
                return await interaction.response.send_message(f"You don't have `{count}` no. of {name} :{name}: in your inventory\nType /hunt to catch more",ephemeral=True)
            
            offer = count*random.randrange(32,45)
            items = [name for i in range(count)]
            embed = discord.Embed(description = f"{buyer} is offering you **{offer}** {self.bot.emotes['credits']} for {count} x {name.title()} :{name}:",color = random.choice(self.bot.colors))
            desc = f"Sold {count} x {name.title()} :{name}: for **{offer}** {self.bot.emotes['credits']}"
        embed.set_footer(text = "Rates of items keep fluctuating")
        embed.set_author(name = f"Offer for {interaction.user.name}",icon_url=interaction.user.display_avatar.url)
        offerview = Offer(30,interaction,offer,embed,desc)
        await interaction.response.send_message(embed=embed,view=offerview)
        result = await offerview.wait()
        if not result:
            if offerview.ans==True:
                await self.bot.add(id,offer)
                for i in items:
                    inventory.remove(i)
                await self.bot.db.execute("UPDATE users SET inventory = $1 WHERE userid = $2",inventory,id)
    
    
    @sell.command(description="Sale off Dig item(s)")
    @app_commands.describe(name="Item name followed by amount with space, ex 'soccer 1' or 'all'")
    async def items(self,interaction:discord.Interaction,name:str):
        id = interaction.user.id
        if id in trades:
            return await interaction.response.send_message("Please complete the previous trade to start a new one",ephemeral=True)
        await self.bot.check(id)
        data = await self.bot.data(id)
        inventory = data[2]
        dinv = [i for i in inventory if i in dig]
        buyer = random.choice(names)

        item = name.lower().strip()
        if len(dinv)==0: return await interaction.response.send_message("You don't have anything in your digging inventory :(\nType /dig to start digging items or collectables and earn credits",ephemeral=True)
    
        if item == "all":
            offer = len(dinv)*random.randrange(50,60)
            items = dinv
            embed = discord.Embed(description = f"{buyer} is offering you **{offer}** {self.bot.emotes['credits']} for **All** [x{len(dinv)}] of your item(s)",color = random.choice(self.bot.colors))
            desc = f"Sold all digging items for **{offer}** {self.bot.emotes['credits']}"
        else:
            itemvar = item.split()
            name = itemvar[0]
            if name not in dig:
                return await interaction.response.send_message(f"No item named `{name}`, make sure you didn't have a typo",ephemeral=True)
            elif name not in dinv: 
                return await interaction.response.send_message(f"You don't have **{name.title()}** :{name}: in your inventory\nType /dig to start collecting items",ephemeral=True)
            
            if len(itemvar)>1:
                try:    
                    count = int(itemvar[1])
                except:
                    if itemvar[1]=="all":
                        count = len([i for i in dinv if i==name])
                    else: return await interaction.response.send_message(embed=self.wrongformat)
            else: count = len([i for i in dinv if i==name])

            if count>len([i for i in dinv if i==name]):
                return await interaction.response.send_message(f"You don't have `{count}` no. of {name} :{name}: in your inventory\nType /dig to collect more",ephemeral=True)
            
            offer = count*random.randrange(50,60)
            items = [name for i in range(count)]
            embed = discord.Embed(description = f"{buyer} is offering you **{offer}** {self.bot.emotes['credits']} for {count} x {name.title()} :{name}:",color = random.choice(self.bot.colors))
            desc = f"Sold {count} x {name.title()} :{name}: for **{offer}** {self.bot.emotes['credits']}"
        embed.set_footer(text = "Rates of items keep fluctuating")
        embed.set_author(name = f"Offer for {interaction.user.name}",icon_url=interaction.user.display_avatar.url)
        offerview = Offer(30,interaction,offer,embed,desc)
        await interaction.response.send_message(embed=embed,view=offerview)
        result = await offerview.wait()
        if not result:
            if offerview.ans==True:
                await self.bot.add(id,offer)
                for i in items:
                    inventory.remove(i)
                await self.bot.db.execute("UPDATE users SET inventory = $1 WHERE userid = $2",inventory,id)
    
        
    @sell.command(description="Sell your Collectable(s) [fixed prices]")
    @app_commands.describe(name="Select the collectable(s) you want to sell")
    async def collectables(self,interaction:discord.Interaction,name:Literal[tuple(["All collectables"]+list(collectables.keys()))], amount:Optional[app_commands.Range[int,1,999]]=None):
        
        id = interaction.user.id
        await self.bot.check(id)
        data = await self.bot.data(id)
        inventory = data[2]
        userC = [i for i in inventory if i in list(collectables.keys())]

        if len(userC)==0: return await interaction.response.send_message("You don't have any collectables :(\nType /dig and invest more credits to gain collectables",ephemeral=True)
    
        if name=="All collectables":
            price = sum([collectables[i] for i in userC])
            text = "\n".join([f"{i.title()} :{i}: x {inventory.count(i)} : **{collectables[i]*inventory.count(i)}** {self.bot.emotes['credits']}" for i in set(userC)])
            embed = discord.Embed(title = "Sold all collectable(s)",description=f"{interaction.user.name} sold ALL [x{len(userC)}] collectable(s) for **{price}** {self.bot.emotes['credits']}\n{text}",color = random.choice(self.bot.colors))
            for i in userC:
                inventory.remove(i)
            await self.bot.add(id,price)
        else: 
            if name not in inventory:
                return await interaction.response.send_message(f"You don't have **{name.title()}** :{name}: collectable in your inventory\nType /dig to start collecting 'em",ephemeral=True)
            amount = amount or len([i for i in userC if i==name])
            if amount>len([i for i in userC if i==name]):
                return await interaction.response.send_message(f"You don't have `{amount}` no. of {name} :{name}: in your inventory\nType /dig to collect more",ephemeral=True)

            price = amount*collectables[name]
            text = f"{name.title()} :{name}: x {amount} : {collectables[name]*amount} {self.bot.emotes['credits']}"
            embed = discord.Embed(title = "Sold collectable(s)",description=f"{interaction.user.name} sold x{amount} collectable(s) for **{price}** {self.bot.emotes['credits']}\n{text}",color = random.choice(self.bot.colors))
            for i in range(amount):
                inventory.remove(name)
            await self.bot.add(id,price)

        embed.timestamp = datetime.datetime.utcnow()
        await self.bot.db.execute("UPDATE users SET inventory = $1 WHERE userid = $2",inventory,id)
        await interaction.response.send_message(embed = embed)

    @app_commands.command(description="What's there in your/others inventory? let's find out")
    @app_commands.describe(member="Mention the member (leave this parameter if you want to check yours)")
    async def inventory(self,interaction:discord.Interaction,member:Optional[discord.Member]=None):
        member = member or interaction.user
        if member.bot: return await interaction.response.send_message("C'mon you are supposed to select a living being, not bot lol",ephemeral=True)
        id = member.id
        data = await self.bot.data(id)
        inventory = data[2]
        if not inventory:return await interaction.response.send_message(f"{member.name} doesn't has anything in their inventory :(",ephemeral=True)
        
        all = [[i for i in inventory if i in fishes],[i for i in inventory if i in animals],[i for i in inventory if i in dig],[i for i in inventory if i in list(collectables.keys())]]
        heads = ['Fish inventory','Hunt inventory','Dig inventory','Collectables']
        embeds = []
        for i in range(len(all)):
            if len(all[i])<1: continue
            item_names = "\n\n".join([f"{k.title()} :{k}:" for k in set(all[i])])
            item_counts = "\n\n".join([f"`{all[i].count(k)}`" for k in set(all[i])])
            embed = discord.Embed(title = heads[i],color=random.choice(self.bot.colors),timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Name",value = item_names)
            embed.add_field(name="Amount",value = item_counts,inline=True)
            embed.set_author(name=member.name,icon_url=member.display_avatar.url)
            embed.set_footer(text = f"Sell these items for credits by /sell")
            embeds.append(embed)
        
        if len(embeds)==0: return await interaction.response.send_message(f"{member.name} doesn't has anything in their inventory :(",ephemeral=True)
        
        if len(embeds)>1:
            await interaction.response.send_message(embed=embeds[0],view=ButtonMenu(embeds,15,interaction,True))
        else:
            await interaction.response.send_message(embed=embeds[0])
           
        
            
        


async def setup(bot):
    await bot.add_cog(Economy(bot), guilds = [discord.Object(id=775940596279410718)])

