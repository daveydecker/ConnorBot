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
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
import asyncio
load_dotenv()
imgExtension = ("png", "jpeg", "jpg", "gif")
images = list()
HA_URL = os.getenv('HA_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
BOT_Token = os.getenv('BOT_TOKEN')
CONNOR_ID = 705138845036970078
sensorFile = "sensor.en.json"
number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


with open(sensorFile, 'r') as file:
    sensorData = json.load(file)

def appendImages(directory="./images"):
    images.clear()
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
        if (item != None) and (name != "null") and (item.get('type', {}).get('value') == "outfit") and (item.get('images', {}).get('featured') or item.get('images', {}).get('icon')) and (not any(substring in name for substring in bad)):
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
    if arg1 == "images":
        imagetense = "images" if len(images) != 1 else "image"
        await ctx.send(f"There is currently {len(images)} {imagetense} of me saved")
    else:
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
                lastUpdated = datetime.fromisoformat(str(weightSensor.last_updated))
                unix = int(lastUpdated.timestamp())
                #dateNow = datetime.now(ZoneInfo("America/New_York"))
                #diff = relativedelta(dateNow, lastUpdated)
                #minutes = diff.years * 525600 + diff.months * 43800 + diff.weeks * 10080 + diff.days * 1440 + diff.hours * 60 + diff.minutes
                #tense = "minute" if minutes == 1 else "minutes"
                await ctx.send(f"The weight of el gato is {weightSensor.state} lbs. Last updated: <t:{unix}:R>")
            elif arg1.lower() == "visits":
                visitsCount = client.get_state(entity_id="sensor.millie_visits_today")
                times = "times" if int(visitsCount.state) > 1 or int(visitsCount.state) == 0 else "time"
                await ctx.send(f"El gato has visited the litter box {visitsCount.state} {times} today")
            elif arg1.lower() == "cycle":
            #     statusCode = client.get_state(entity_id="sensor.litter_robot_4_status_code")
            #     if statusCode.state == "rdy":
            #         client.trigger_service(domain="vacuum", service="start", entity_id="vacuum.litter_robot_4_litter_box")
                await ctx.send("Cycling litter box")
            #     elif statusCode.state == "cd" or statusCode.state == "csi":
            #         await ctx.send("Cannot cycle. El gato is inside the box")
            #     else:
            #         await ctx.send(f"Litter Box cannot be cycled. Reason: {sensorData["state"]["litterrobot__status_code"][statusCode.state]}")
            # else:
            #     await ctx.send("Invalid command")
    except Exception as e:
        print(e)
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

@bot.command()
async def ip(ctx):
    r = requests.get("https://icanhazip.com")
    await ctx.send(r.text)

@bot.command()
async def timetil(ctx, arg1="30"):
    try:
        arg1 = int(arg1)
        yearFinal = 2005 + arg1
        if yearFinal < datetime.now().year:
            await ctx.send("Invalid age")
            return
        dateFinal = datetime(yearFinal, 8, 30, 0, 0, 0)
        dateNow = datetime.now()
        timetil30 = relativedelta(dateFinal, dateNow)
        years = "year" if timetil30.years == 1 else "years"
        months = "month" if timetil30.months == 1 else "months"
        days = "day" if timetil30.days == 1 else "days"
        hours = "hour" if timetil30.hours == 1 else "hours"
        minutes = "minute" if timetil30.minutes == 1 else "minutes"
        seconds = "second" if timetil30.seconds == 1 else "seconds"
        await ctx.send(f"Connor Sherman will be turning {arg1} in {timetil30.years} {years}, {timetil30.months} {months}, {timetil30.days} {days}, {timetil30.hours} {hours}, {timetil30.minutes} {minutes}, {timetil30.seconds} {seconds}", file=discord.File("bunny.png"))
    except:
        await ctx.send("Enter a number")

@bot.command()
async def ow(ctx):
    num = random.randint(1, 2)
    print(num)
    if num == 1:
        file = "ConnorOverwatch.gif"
    else:
        file = "ConnorBomb.gif"
    await ctx.send(f"<@{CONNOR_ID}>", file=discord.File(file))

# Game Deal Block
def search(title):
    headers = {"User-Agent": "ConnorBot/1.0 (daveydecker3.0@gmail.com)"}
    params = {"title": title}
    r = requests.get(url="https://www.cheapshark.com/api/1.0/games", headers=headers, params=params)
    return r

def searchId(id):
    headers = {"User-Agent": "ConnorBot/1.0 (deveydecker3.0@gmail.com)"}
    params = {"id": id}
    r = requests.get(url="https://www.cheapshark.com/api/1.0/games", headers=headers, params=params)
    return r

def storesMap():
    headers = {"User-Agent": "ConnorBot/1.0 (deveydecker3.0@gmail.com)"}
    r = requests.get(url="https://www.cheapshark.com/api/1.0/stores", headers=headers)
    stores = r.json()
    map = {}
    for store in stores:
        map[store['storeID']] = store['storeName']
    return map

@bot.command()
async def sale(ctx, *, title):
    response = search(title)
    games = response.json()
    if len(games) == 0:
        await ctx.send("No games found")
        return
    embed = discord.Embed(
        title="Found Games",
        description="React with the game you want to search the sale of",
        color=discord.Color.blue()
    )
    gameIds = []
    gameTitles = []
    pickedIndex = None
    i = 0
    for game in games:
        if i > 4:
            break
        embed.add_field(name=f"{number_emojis[i]} {game['external']}", value=" ", inline=False)
        gameIds.append(game['gameID'])
        gameTitles.append(game['external'])
        i += 1
    if len(games) > 1:
        msg = await ctx.send(embed=embed)
        valid_reactions = []
        for j in range(i):
            await asyncio.gather(msg.add_reaction(number_emojis[j]))
            valid_reactions.append(number_emojis[j])
        def check(reaction, user):
            return (user == ctx.author
                    and str(reaction.emoji) in valid_reactions
                    and reaction.message.id == msg.id
                    )
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
            k = 0
            for item in number_emojis:
                if str(reaction.emoji) == item:
                    pickedIndex = k
                    break
                k += 1
        except TimeoutError:
            await msg.delete()
            return
        if pickedIndex == None:
            await ctx.send("No game selected")
            return
        await msg.delete()
    else:
        pickedIndex = 0
    title = gameTitles[pickedIndex]
    GameID = gameIds[pickedIndex]
    response = searchId(GameID)
    game_id = response.json()
    embed = discord.Embed(
        title=f"Results for {title}",
        color=discord.Color.blue()
    )
    embed.add_field(name=f"Cheapest Price Ever: ${game_id['cheapestPriceEver']['price']} was <t:{game_id['cheapestPriceEver']['date']}:R>",
                    value=" ", inline=False)
    deals = {}
    for deal in game_id['deals']:
        if len(deals) > 5 or float(deal['savings']) == 0:
            break
        deals[deal['storeID']] = deal['price']
    if len(deals) == 0:
        embed.add_field(name="No deals found", value=" ", inline=False)
    map = storesMap()
    for GameID in deals:
        embed.add_field(name=f"${deals[GameID]} at {map[GameID]}", value=" ", inline=False)
    await ctx.send(embed=embed)
bot.run(BOT_Token)