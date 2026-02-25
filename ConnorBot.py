from homeassistant_api import Client
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
HA_URL = os.getenv('HA_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
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
@bot.command()
async def cat(ctx, *, arg1="weight"):
    with Client(HA_URL, ACCESS_TOKEN) as client:
        if arg1.lower() == "weight":
            weightSensor = client.get_state(entity_id="sensor.millie_weight")
            await ctx.send(f"The weight of the cat is {weightSensor.state}")
        if arg1.lower() == "visits":
            visitsCount = client.get_state(entity_id="sensor.millie_visits_today")
            times = "times" if int(visitsCount.state) > 1 or int(visitsCount.state) == 0 else "time"
            await ctx.send(f"The cat has visited the litter bot {visitsCount.state} {times} today")
        if arg1.lower() == "cycle":
            client.trigger_service(domain="vacuum", service="start", entity_id="vacuum.litter_robot_4_litter_box")
            await ctx.send("Cycling litter box")
bot.run(BOT_Token)