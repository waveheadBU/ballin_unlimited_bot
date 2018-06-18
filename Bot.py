import random
import asyncio
import aiohttp
import json
import discord
import requests
import bs4
import collections
from discord import Game
from discord.ext import commands

BOT_PREFIX = ("?", "!")
TOKEN = 'NDU1OTE3MzAyMDM0OTg5MDU2.DgQXUw.ZTSeJy_ApBpYZ1AT-U8LwIJhAo8'
WeatherReport = collections.namedtuple('WeatherReport',
                                       'temp, scale, cond, loc')

client = discord.Client()
client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)


@client.command()
async def add(left: int, right: int):
    """Adds two numbers together."""
    await client.say(left + right)


@client.command(description='Provides the weather for a given zipcode, e.g. !weather 90210')
async def weather(zipcode: str):
    # print the header
    # print_the_header()
    # get zip code from user
    # code = input('What zip code do you want the weather for (97201)? ')
    # get html from web
    html = get_html_from_web(zipcode)
    # parse the html
    report = get_weather_from_html(html)
    # display the forecast
    # print('The temp in {} is {} {} and {}'.format(
    #     report.loc,
    #     report.temp,
    #     report.scale,
    #     report.cond
    # ))
    await client.say('The temp in {} is {} {} and {} '.format(
        report.loc,
        report.temp,
        report.scale,
        report.cond
    ))


# def print_the_header():
#     print('------------------------------------------------------')
#     print('                     Weather App                      ')
#     print('------------------------------------------------------')
#     print()


def get_html_from_web(zipcode):
    url = 'http://www.wunderground.com/weather-forecast/{}'.format(zipcode)
    response = requests.get(url)
    # print(response.status_code)
    # print(response.text[0:250])

    return response.text


def get_weather_from_html(html):
    # cityCSS = '.region-content-header h1'
    # weatherScaleCSS = '.wu-unit-temperature.wu-label'
    # weatherTempCSS = '.wu-unit-temperature.wu-value'
    # weatherConditionCSS = '.condition-icon'

    soup = bs4.BeautifulSoup(html, 'html.parser')
    # print(soup)
    loc = soup.find(class_="region-content-header").find('h1').get_text()
    condition = soup.find(class_='condition-icon').get_text()
    temp = soup.find(class_='wu-unit-temperature').find(class_='wu-value').get_text()
    scale = soup.find(class_='wu-unit-temperature').find(class_='wu-label').get_text()

    loc = cleanup_text(loc)
    condition = cleanup_text(condition)
    temp = cleanup_text(temp)
    scale = cleanup_text(scale)

    # print(temp, scale, condition, loc)
    # return temp, scale, condition, loc
    report = WeatherReport(temp=temp, scale=scale, cond=condition, loc=loc)
    return report


def cleanup_text(text: str):
    if not text:
        return text

    text = text.strip()
    return text


@client.command()
async def roll(dice: str):
    """Rolls a dice in NdN format"""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await client.say('Format has to be NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await client.say(result)


@client.command(description='For when you wanna settle the score some other way')
async def choose(*choices: str):
    """Chooses between multiple items."""
    await client.say(random.choice(choices))


@client.command(description='Chooses what to eat for lunch.',
                pass_context=True)
async def lunch(context):
    """Chooses what to eat for lunch."""
    lunch_selections = [
        "Antoni's",
        "Hub City Diner",
        "Popeye's",
        "Masalas",
        "Raising Canes",
        "Cafe Lola",
        "Bon Temps Grill",
    ]
    await client.say(random.choice(lunch_selections) + ", " + context.message.author.mention)


@client.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked."""
    if ctx.invoked_subcommand is None:
        await client.say('No, {0.subcommand_passed} is not cool'.format(ctx))


@cool.command(name='bot')
async def _client():
    """Is the bot cool?"""
    await client.say('Yes, the bot is cool')


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
    ]
    await client.say(random.choice(possible_responses) + ", " + context.message.author.mention)


@client.command(pass_context=True)
async def hello(context):
    await client.say('Hello ' + context.message.author.mention)


@client.command()
async def square(number):
    squared_value = int(number) * int(number)
    await client.say(str(number) + " squared is " + str(squared_value))


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with humans"))
    print("Logged in as " + client.user.name)


@client.command()
async def bitcoin():
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        await client.say("Bitcoin price is: $" + response['bpi']['USD']['rate'])


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
