# R.A.M - Discord Interface

import discord
from discord.ext import commands
import config
import asyncio
import aiohttp, json
from datetime import datetime
from dateutil import parser

bot = commands.Bot(command_prefix=config.prefix)

async def get_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{config.api_loc}/aggregates") as resp:

            if resp.status == 200:
                j = json.loads(await resp.text())
                return j

@bot.event
async def on_ready():
    print(f"Logged in. Username: {bot.user}")
    bot.loop.create_task(update_status())

@bot.command()
async def server(ctx):
    """
    Get R.A.M.'s current server"""

    data = await get_data()

    if not data['ram_online']: 
        await ctx.channel.send(":x: R.A.M. Is currently offline. Check back later!")
        return

    await ctx.channel.send(f"R.A.M is on server: {data['ram_server']}")

@bot.command()
async def location(ctx):
    """
    Get R.A.M.'s current location"""

    data = await get_data()

    if not data['ram_online']: 
        await ctx.channel.send(":x: R.A.M. Is currently offline. Check back later!")
        return

    await ctx.channel.send(f"R.A.M's currently in: {data['ram_location']}")

@bot.command()
async def status(ctx):
    """
    Get all stats from R.A.M."""

    data = await get_data()
    
    if not data['ram_online']:
        await ctx.channel.send(":x: R.A.M. Is currently offline. Check back later!")
        return


    # Create the information embed
    embed = discord.Embed(title="R.A.M. Status Tracker", 
    timestamp=parser.parse(data['last_uplink_time']),
    colour=discord.Colour(0x18cc0f))
    embed.set_footer(text="Data last updated")

    if data['ram_parameters']['vehicle']['data'] == "Truck":
        embed.set_thumbnail(url=config.images['vehicle_truck'])
    else:
        embed.set_thumbnail(url=config.images['vehicle_car'])

    x = data['ram_parameters'] # Laziness 100

    embed.add_field(name="🌐 Server", value=data['ram_server'], inline=True)
    embed.add_field(name="🗺 Location", value=data['ram_location'], inline=True)
    embed.add_field(name="📋 Task", value=x['task']['data'], inline=False)
    embed.add_field(name="🚗 Vehicle Mode", value=x['mode']['data'], inline=True)
    embed.add_field(name="🚙 Vehicle Type", value=x['vehicle']['data'], inline=True)
    embed.add_field(name="📌 Drive Path", value=x['path']['data'], inline=False)
    embed.add_field(name="⌨ Vehicle Control Mode", value=x['control_mode']['data'])
    embed.add_field(name="💥 Vehicle Damage", value=x['vehicle_damage']['data'])

    await ctx.channel.send("R.A.M. Status", embed=embed)

async def update_status():
    while True:
        print("A")
        if bot.user: 
            print("B")
            data = await get_data()
            
            if data['ram_online']:
                game = discord.Game(f"on {data['ram_server']} in {data['ram_location']}")
                await bot.change_presence(status=discord.Status.online, activity=game)
            else:
                await bot.change_presence(status=discord.Status.dnd)

            print("C")

        await asyncio.sleep(60)

bot.run(config.token)