from homeassistant_api import Client
from discord.ext import commands
import discord
import os
import random
import uuid
from dotenv import load_dotenv
import requests
import json
import difflib
load_dotenv()
imgExtension = ("png", "jpeg", "jpg", "gif")
images = list()
HA_URL = os.getenv('HA_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
BOT_Token = os.getenv('BOT_TOKEN')
CONNOR_ID = 705138845036970078
sensorFile = "sensor.en.json"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


with open(sensorFile, 'r') as file:
    sensorData = json.load(file)

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

def downloadSkin(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open("fortSkin.png", "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

def appendCharacters(fortData):
    fortItems = fortData['data']
    characters = []
    names = []
    for item in fortItems:
        name = item['name'].lower()
        bad = ["tbd", "set_"]
        if (item.get('type', {}).get('value') == "outfit") and (item.get('images', {}).get('featured') or item.get('images', {}).get('icon')) and (not any(substring in name for substring in bad)):
            characters.append(item)
            names.append(name)
    return characters, names

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
async def connor(ctx, *, arg1="get on the game bro"):
    await ctx.send(content=f"<@{CONNOR_ID}> {arg1}", file=discord.File(pickImage()))

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
    try:
        with Client(HA_URL, ACCESS_TOKEN) as client:
            if arg1.lower() == "weight":
                weightSensor = client.get_state(entity_id="sensor.millie_weight")
                await ctx.send(f"The weight of el gato is {weightSensor.state} lbs")
            elif arg1.lower() == "visits":
                visitsCount = client.get_state(entity_id="sensor.millie_visits_today")
                times = "times" if int(visitsCount.state) > 1 or int(visitsCount.state) == 0 else "time"
                await ctx.send(f"El gato has visited the litter box {visitsCount.state} {times} today")
            elif arg1.lower() == "cycle":
                statusCode = client.get_state(entity_id="sensor.litter_robot_4_status_code")
                if statusCode.state == "rdy":
                    client.trigger_service(domain="vacuum", service="start", entity_id="vacuum.litter_robot_4_litter_box")
                    await ctx.send("Cycling litter box")
                elif statusCode.state == "cd" or statusCode.state == "csi":
                    await ctx.send("Cannot cycle. El gato is inside the box")
                else:
                    await ctx.send(f"Litter Box cannot be cycled. Reason: {sensorData["state"]["litterrobot__status_code"][statusCode.state]}")
            else:
                await ctx.send("Invalid command")
    except:
        await ctx.send("An error has occured")

@bot.command()
async def fortnite(ctx, *, arg1="random"):
    fortResponse = requests.get("https://fortnite-api.com/v2/cosmetics/br")
    if (fortResponse.status_code != 200):
        await ctx.send(f"Something went wrong. status code: {fortResponse.status_code}")
        return
    
    fortData = fortResponse.json()
    characters, names = appendCharacters(fortData)
    if (arg1.lower() == "random"):
        randomChar = random.choice(characters)
        url = randomChar['images']['featured'] if randomChar.get('images', {}).get('featured') else randomChar['images']['icon']
        downloadSkin(url)
        await ctx.send(f"Here is your random Fortnite Skin:\nName: {randomChar['name']}\nDescription: {randomChar['description']}\n{randomChar['introduction']['text']}", file=discord.File("fortSkin.png"))
        os.remove("fortSkin.png")
    else:
        matches = difflib.get_close_matches(arg1.lower(), names, n=1, cutoff=0.6)
        if matches:
            characterName = matches[0]
            index = names.index(characterName)
            character = characters[index]
            url = character['images']['featured'] if character.get('images', {}).get('featured') else character['images']['icon']
            downloadSkin(url)
            await ctx.send(f"Here is your Fortnite Skin:\nName: {character['name']}\nDescription: {character['description']}\n{character['introduction']['text']}", file=discord.File("fortSkin.png"))
            os.remove("fortSkin.png")
        else:
            await ctx.send("Skin could not be found")
    
    
bot.run(BOT_Token)