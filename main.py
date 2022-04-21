import discord
from discord.ext import commands
import json
import os
import random
from keep_alive import keep_alive
from discord.utils import get

client = commands.Bot(command_prefix='e!')

mainshop = [{
    "name": "tavern-Table",
    "price": 25,
    "description": "A table at the tavern, for 3 days!"
}, {
    "name": "bank-security",
    "price": 100,
    "description": "10 more security points!"
}, {
    "name": "toast",
    "price": 3,
    "description": "Some freshly baked toast"
}, {
    "name": "beer",
    "price": 2,
    "description": "Tasty beer for you to enjoy"
}, {
    "name": "apartment-room",
    "price": 150,
    "description": "A place where you can live"
}, {
    "name": "huge-mansion",
    "price": 500,
    "description": "Gives your house a place in this town"
}, {
    "name": "something you can't buy",
    "price": 0,
    "description": "Try to buy this"  
}, {
    "name": "sweet-jam",
    "price": 1,
    "description": "Pairs really good with toast"
}, {
    "name": "Phone",
    "price": 20,
    "description": "The brand new phone"
}, {
    "name": "ticket",
    "price": 100,
    "description": "ticket to visit the brand new museum!"
}, {
    "name": "house",
    "price": 250,
    "description": "A place for you to live that is smaller than a mansion"
}]

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name='Dighfuji'))
    print("Ready")


@client.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = round(users[str(user.id)]["wallet"])
    bank_amt = round(users[str(user.id)]["bank"])

    em = discord.Embed(title=f"{ctx.author.name}'s balance",
                       color=discord.Color.blue())
    em.add_field(name="Wallet balance", value=wallet_amt)
    em.add_field(name="Bank balance", value=bank_amt)

    await ctx.send(embed=em)

@client.command()
async def sec(ctx):
    print(1)
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    print(ctx.author, "checked the security")

    sec = round(users[str(user.id)]["sec"])
    print(sec)

    await ctx.send(f"You have {sec} security points")
    

@client.command()
async def gross(ctx, earn=None):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    earnings = int(earn)

    await ctx.send(f"You earned {earnings} coins!")

    users[str(user.id)]["wallet"] += earnings

    with open("bank.json", "w") as f:
        json.dump(users, f)


@client.command()
async def modrole(ctx):
    if get(ctx.guild.roles, name="senior"):
        await ctx.send("exception sucess, role created")
        print("001")
    else:
        await ctx.guild.create_role(name="senior",
                                    colour=discord.Colour(0x0062ff))
        print("Role created")


@client.command()
async def pay(ctx, user: discord.Member, amount=None):
    try:
        role = discord.utils.find(lambda r: r.name == 'senior',
                                  ctx.message.guild.roles)
        auth = ctx.author
        if role in auth.roles:
            data = await get_bank_data()

            earnings = int(amount)
            await update_bank(user, earnings)

            await ctx.send(f"You have paid {user} {earnings} coins!")
        else:
            await ctx.send("You don't have senior role!")
    except:
        await modrole(ctx)
        role = discord.utils.find(lambda r: r.name == 'senior',
                                  ctx.message.guild.roles)
        auth = ctx.author
        if role in auth.roles:
            data = await get_bank_data()

            earnings = int(amount)
            await update_bank(user, earnings)

            await ctx.send(f"You have paid {user} {earnings} coins!")
        else:
            await ctx.send("You don't have senior role!")


@client.command()
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = round(int(amount))

    if amount > bal[1]:
        await ctx.send("You don't have that much money!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, "bank")

    await ctx.send(f"You withdrew {amount} coins!")


@client.command()
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = round(int(amount))

    if amount > bal[0]:
        await ctx.send("You don't have that much money!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive")
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, "bank")

    await ctx.send(f"You deposited {amount} coins!")


@client.command()
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)

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

    await update_bank(ctx.author, -1 * amount, "bank")
    await update_bank(member, amount, "bank")

    await ctx.send(f"You sent {amount} coins to {member}!")


@client.command()
async def slots(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = round(float(amount), 2)
    if amount > bal[0]:
        await ctx.send("You don't have that much money!")
        return
    if amount < 0:
        await ctx.send("Amount must be positive")
        return
    final = []
    for i in range(3):
        a = random.choice(["X", "O", "Q"])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[2] or final[0] == final[1] and final[0] == final[2]:
        await update_bank(ctx.author, int(2 * amount))
        await ctx.send("You won!")
    else:
        await update_bank(ctx.author, int(-1 * amount))
        await ctx.send("You lost!")


@client.command()
async def rob(ctx, member: discord.Member):
    try:
        await open_account(ctx.author)
        await open_account(member)

        bal = await update_bank(member)

        if bal[0] < 5:
            await ctx.send("It's not worth it!")
            return

        earnings = random.randrange(0, round(int(bal[0] * 0.75)))

        await update_bank(ctx.author, earnings)
        await update_bank(member, -1 * earnings)
        earnings = int(earnings)

        await ctx.send(f"You robbed {earnings} coins from {member}!")

    except:
        await ctx.send("One argument, the member, is missing!")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command is still on cooldown, please try again in {:.2f} seconds'.format(
            error.retry_after)
        await ctx.send(msg)


@client.command()
@commands.cooldown(2, 30, commands.BucketType.user)
async def heist(ctx, member: discord.Member):
    try:
        await open_account(ctx.author)
        await open_account(member)

        bal = await update_bank(member)
        pos = random.randrange(0, bal[2] / 2)
        dos = random.randrange(0, bal[2] / 2)
        print(pos, dos)
        await ctx.send("You attempted to break into the bank...")
        print('command exe')

        if pos == dos:
            await ctx.send("You broke into the bank!")

            earnings = random.randrange(0, round(int(bal[1] * 0.75)))
            earnings = int(earnings)

            await update_bank(ctx.author, earnings)
            await update_bank(member, -1 * earnings)

            await ctx.send(f"You robbed {earnings} coins from {member}!")
        else:
            await ctx.send("Your attempt was unsuccessful!")

    except:
        await ctx.send("An error has occured!")


@client.command()
async def shop(ctx):
    em = discord.Embed(title="Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        description = item["description"]
        em.add_field(name=name, value=f"${price} | {description}")

    await ctx.send(embed=em)


@client.command()
async def buy(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(
                f"You don't have enough money in your wallet to buy {amount} {item}"
            )
            return
    if res[0]:
        if res[1] == 0:
            await ctx.send(f"You just bought {amount} {item}")
        if res[1] == 1:
            secure = 10 * amount

            print(secure)
            await update_bank(ctx.author, secure, "sec")
            new_bal = await update_bank(ctx.author)

            dict_bk = mainshop[1]
            price_bk = dict_bk["price"]

            await update_bank(ctx.author, price_bk * amount * -1)

            await ctx.send(f"You just bought {secure} bank security points!")
            await ctx.send(f"You now have {new_bal[2]} bank security points")


@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    em = discord.Embed(title="Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name=name, value=amount)

    await ctx.send(embed=em)


async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price * amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0] < cost:
        return [False, 2]
    if item_name == "bank-security":
        return [True, 1]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["bag"] = [obj]

    with open("bank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost * -1, "wallet")

    return [True, 0]


@client.command()
async def sell(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1] == 3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price == None:
                price = round(0.8 * item["price"])
            break

    if name_ == None:
        return [False, 1]

    cost = price * amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open("bank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]


async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 10
        users[str(user.id)]["sec"] = 10

    with open("bank.json", "w") as f:
        users = json.dump(users, f)

    return True


async def get_bank_data():
    with open("bank.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode="wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("bank.json", "w") as f:
        json.dump(users, f)

    bal = [
        users[str(user.id)]["wallet"], users[str(user.id)]["bank"],
        users[str(user.id)]["sec"]
    ]
    return bal


keep_alive()
client.run(os.getenv('TOKEN'))
