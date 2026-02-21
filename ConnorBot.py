from discord.ext import commands
import discord
import os
import random
import uuid
from dotenv import load_dotenv
import requests
import json
load_dotenv()
imgExtension = ("png", "jpeg", "jpg", "gif")
images = list()
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
BOT_Token = os.getenv('BOT_TOKEN')
CONNOR_ID = 705138845036970078

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def appendImages(directory="./images"):
    for i in os.listdir(directory):
        if i.endswith(imgExtension):
            images.append(directory + "/" + i)

def pickImage():
    return random.choice(images)

def getWeather(location="Atlanta"):
    _location = "Kyoto" if location.lower() == "home" else location
    api_url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_TOKEN}&q={_location}&aqi=no"
    return requests.get(api_url)


@bot.event
async def on_ready():
    appendImages()
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.attachments and message.channel.id == 1472540713521643541:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(imgExtension):
                attachment.filename = f"{uuid.uuid4()}{attachment.filename}"
                file_path = os.path.join("./images", attachment.filename)
                await attachment.save(file_path)
                images.append(file_path)
                print(f"{file_path} downloaded")
    await bot.process_commands(message)
@bot.command()
async def connor(ctx):
    await ctx.send(content=f"<@{CONNOR_ID}> get on the game bro", file=discord.File(pickImage()))

@bot.command()
async def weather(ctx, *, arg1="Atlanta"):
    response = getWeather(arg1)
    data = response.json()
    if response.status_code == 200:
        await ctx.send(content=f"My name is Connor Sherman and the weather in {data['location']['name']} is {data['current']['temp_f']} degrees farenheit and {data['current']['condition']['text']}", file=discord.File(pickImage()))
    elif response.status_code == 400:
        await ctx.send(content=f"{data['error']['message']}")
    else:
        await ctx.send(content="Yo something went wrong lowkey")
bot.run(BOT_Token)