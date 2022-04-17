import discord
from discord.ext import commands
import json
import os
from keep_alive import keep_alive

client = commands.Bot(command_prefix = "e!")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Dighfuji'))
    print("Ready")

@client.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s balance",color = discord.Color.blue())
    em.add_field(name = "Wallet balance",value = wallet_amt)
    em.add_field(name = "Bank balance",value = bank_amt)
    await ctx.send(embed = em)

    
    @client.command()
    async def gross(ctx):
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()
    
        earnings = 1
    
        await ctx.send(f"You earned {earnings} coins!")
    
        users[str(user.id)]["wallet"] += earnings
        
        with open("bank.json","w") as f:
            json.dump(users,f)

@client.command()
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You don't have that much money!")
        return 
    if amount < 0:
        await ctx.send("Amount must be positive")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")

    await ctx.send(f"You withdrew {amount} coins!")

@client.command()
async def deposit(ctx,amount = None):
    await open_account(ctx.author)
    
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("You don't have that much money!")
        return 
    if amount < 0:
        await ctx.send("Amount must be positive")
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,"bank")

    await ctx.send(f"You deposited {amount} coins!")


async def open_account(user):
    
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("bank.json","w") as f:
        users = json.dump(users,f)

    return True

async def get_bank_data():
    with open("bank.json","r") as f:
        users = json.load(f)

    return users

async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change
    
    with open("bank.json","w") as f:
        json.dump(users,f)

    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal









    

keep_alive()
client.run(os.getenv('TOKEN'))