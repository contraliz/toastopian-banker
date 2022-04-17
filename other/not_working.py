import discord
from discord.ext import commands
import os
import json
from keep_alive import keep_alive

currency = "coins"

client = commands.Bot(command_prefix = "e!")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('hi!')

@client.command()
async def open_account(user):
    with open("bank.json", "r") as f:
        users = json.load(f)
    if str(user.id) in users:
        await user.send("You already have an account!")
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("bank.json", "w") as f:
        json.dump(users,f)
        await user.send("Your account has been created!")

    return True

async def balance(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()
    userid = str(ctx.user.id)

    wallet_amt = users[userid]["wallet"]
    bank_amt = users[userid]["bank"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.blue())
    em.add_field(name = "Wallet", value = wallet_amt)
    em.add_filed(name = "Bank", value = bank_amt)
    await ctx.sned(embed = em)

@client.command()
async def earn(ctx, amt):
    await open_account(ctx.author)

    users = await get_bank_data()
    earnings = amt

    await ctx.send(f"Someone gave you {earnings} coins!")
    users[str(ctx.user.id)]["wallet"] += earnings

    with open("bank.json", "w") as f:
        json.dump(users,f)
    
async def get_bank_data():
    with open("bank.json", "r") as f:
        users = json.load(f)

    return users

keep_alive()
client.run(os.getenv('TOKEN'))
