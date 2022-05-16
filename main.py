import discord
from discord.ext import commands, tasks
import os
import random
import requests
import datetime
import time
from datetime import datetime, timedelta
from keep_alive import keep_alive

time_window_milliseconds = 5000
max_msg_per_window = 5
author_msg_times = {}

key=os.getenv('key') # Just some things you might want inside the bot here.
wkey=os.getenv('wkey')

client = discord.Client() # Declaring what the client is.
client = commands.Bot(command_prefix = '$') # Makes the bot's command prefix.
client.remove_command('help') # Removes the auto help command as it can be buggy.

## Hello Images -------------------------------------------------
helloIMG = [
  'https://tenor.com/view/hello-there-private-from-penguins-of-madagascar-hi-wave-hey-there-gif-16043627',
  'https://tenor.com/view/hello-there-baby-yoda-mandolorian-hello-gif-20136589',
  'https://tenor.com/view/hello-hi-minion-gif-16235329',
  'https://tenor.com/view/looney-tunes-daffy-duck-hello-greetings-well-hello-there-gif-17075737',
  'https://tenor.com/view/sidhu-moose-wala-sidhu-moose-bohemia-siddhu-moose-hello-gif-19671770',
  'https://tenor.com/view/uwu-smug-anime-stare-gif-17603924',
  'https://media1.tenor.com/images/4024a12e035e6b1ecb309521540c94e8/tenor.gif?itemid=9374870',
  'https://media1.tenor.com/images/cf7497c6c1e8cdf438c35f14e377105f/tenor.gif?itemid=17282851',
  'https://media1.tenor.com/images/dc5e117fe54160166ca9629c253578f3/tenor.gif?itemid=11600514'
]

def removePre(name):
  newName = ""
  for x in name:
    if x != "!":
      newName = newName + x
  return newName

## Bot Ready ------------------------------------------------------
@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.idle, activity=discord.Game("with a fork and outlet"))
  print('We have logged in as {0.user}'.format(client))

## On Message -------------------------------------------------
@client.event
async def on_message(message):
  if client.user.mentioned_in(message):
        await message.channel.send("Use $commands to see what I can do.")
  global author_msg_counts

  author_id = message.author.id
    # Get current epoch time in milliseconds
  curr_time = datetime.now().timestamp() * 1000

    # Make empty list for author id, if it does not exist
  if not author_msg_times.get(author_id, False):
    author_msg_times[author_id] = []

    # Append the time of this message to the users list of message times
  author_msg_times[author_id].append(curr_time)

    # Find the beginning of our time window.
  expr_time = curr_time - time_window_milliseconds

    # Find message times which occurred before the start of our window
  expired_msgs = [
    msg_time for msg_time in author_msg_times[author_id]
    if msg_time < expr_time
    ]

    # Remove all the expired messages times from our list
  for msg_time in expired_msgs:
    author_msg_times[author_id].remove(msg_time)
    # ^ note: we probably need to use a mutex here. Multiple threads
    # might be trying to update this at the same time. Not sure though.
  if message.author == client.user:
        return
  elif len(author_msg_times[author_id]) >= max_msg_per_window:
    await message.channel.send("STOP SPAMMING MAN! CALM YOURSELF!")
  ## --------------------------------------------------------------
  await client.process_commands(message)

## Read random word from file for Wordle --------------------------
def randomWord():
  lines = open('words.txt').read().splitlines()
  global answer 
  answer = random.choice(lines)

def checkWord(guess):
  result = ""
  for pos, ch_guess, ch_answer in zip(range(5), guess, answer):
    if ch_guess == ch_answer:
      result += ":negative_squared_cross_mark: "
    elif ch_guess not in answer:
      result += ":white_large_square: "
    else:
      result += ":yellow_square: "
  return result   
  
## Wordle --------------------------------------------------------
@client.command()
async def wordle(ctx):
  randomWord()
  print("The word: " + answer)
  await ctx.send("Aight I got a word now start guessing with ``$g guess``")
  
@client.command()
async def g(ctx, msg):
  box = ':negative_squared_cross_mark:'
  if msg.lower() == answer:
    await ctx.send(box + " " + box + " " + box + " " + box + " " + box)
    await ctx.send("Yayy you guessed the word!! \nTo see the word definition type ``$wordDef``")
  else:
    if len(msg) != 5:
      await ctx.send("Your guess must be 5 letters.")
    else:
      result = checkWord(msg.lower())
      await ctx.send(result)

@client.command()
async def giveup(ctx):
  await ctx.send("Unlucky mate. The word was ``{}``. Better luck next time. \nTo see the word definition type ``$wordDef``".format(answer))

@client.command()
async def wordDef(ctx):
  response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/" + answer)
  defin = response.json()
  embed = discord.Embed(title = answer[0].upper() + answer[1:] + " - Definition", description = defin[0]['meanings'][0]['definitions'][0]['definition'], color=0x2ecc71)
  await ctx.send(embed=embed)
  
## Hello ----------------------------------------------------------
@client.command()
async def hello(ctx):
  number = random.randint(1,len(helloIMG) - 1)
  await ctx.send(helloIMG[number])

## Mention ----------------------------------------------------------
@client.command()
async def mention(ctx, *, msg: str):
  name = msg.split(" ", 1)[0]
  count = int(msg.split(" ", 1)[1])
  name = removePre(name)
  if count < 5:
    for x in range(count):
      await ctx.send("{} GUESS WHAT".format(name))
      time.sleep(1)
    number = random.randint(1,len(helloIMG) - 1)
    await ctx.send("hi");
  else:
    await ctx.send("That's too many man, calm down.".format(ctx.author.mention))  

## Coinflip -------------------------------------------------------
@client.command()
async def coinflip(ctx):
  number = random.randrange(1, 3)
  if number == 1:
    await ctx.send("Tails " + ":regional_indicator_t:")
  else:
    await ctx.send("Heads " + ":regional_indicator_h:")

## Random Number Generator -----------------------------------------
@client.command()
async def randnum(ctx, *, msg: str):
  min = int(msg.split(" ", 1)[0])
  max = int(msg.split(" ", 1)[1])
  number = random.randrange(min, max+1)
  await ctx.send("`Random Number: " + str(number) + "`")

## AnimeQuote API --------------------------------------------------------
@client.command()
async def randquote(ctx):
  response = requests.get("https://animechan.vercel.app/api/random")
  quote = response.json()
  embed = discord.Embed(title = quote['anime'] + " - " + quote['character'], description = quote['quote'], color=0x2ecc71)  
  await ctx.send(embed=embed)

@client.command()
async def animequote(ctx, *, msg: str):
  response = requests.get("https://animechan.vercel.app/api/quotes/anime?title="+msg)
  quote = response.json()
  number = random.randrange(0, len(quote)+1)
  embed = discord.Embed(title = quote[number]['anime'] + " - " + quote[number]['character'], description = quote[number]['quote'], color=0xe91e63)  
  await ctx.send(embed=embed)

@client.command()
async def charquote(ctx, msg):
  response = requests.get("https://animechan.vercel.app/api/quotes/character?name="+msg)
  quote = response.json()
  number = random.randrange(0, len(quote)+1)
  embed = discord.Embed(title = quote[number]['anime'] + " - " + quote[number]['character'], description = quote[number]['quote'], color=0xe74c3c)  
  await ctx.send(embed=embed)

## Joke API --------------------------------------------------------
@client.command()
async def joke(ctx):
  response = requests.get("https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun")
  joke_link = response.json()
  if joke_link['type'] == "single":
    await ctx.send(joke_link['joke'])
  else:
    await ctx.send(joke_link['setup'])
    time.sleep(3)
    await ctx.send(joke_link['delivery'])

## List of Commands--------------------------------------------------
@client.command()
async def commands(ctx):
  embed = discord.Embed(title="Help - List of commands", description="This page is for helping you guys understand the commands.", color=0xFFFFF)

  embed.add_field(name = "$commands", value = "This is the help command.")

  embed.add_field(name = "$hello", value = "A greeting.")

  embed.add_field(name = "$joke", value = "Get a joke.")

  embed.add_field(name = "$coinflip", value = "Flip a coin.")

  embed.add_field(name = "$wordle", value = "Generate a new wordle.")

  embed.add_field(name = "$g *word*", value = "After generating a new wordle guess the word.")

  embed.add_field(name = "$giveup", value = "Display the answer to the wordle.")
  
  embed.add_field(name = "$mention *name* *num*", value = "Pings the person a number of times.")
    
  embed.add_field(name = "$randnum *min max*", value = "Random number generator.")

  embed.add_field(name = "$randquote", value = "Random anime quote generator.")

  embed.add_field(name = "$animequote *anime_name*", value = "Generates a quote from that anime.")

  embed.add_field(name = "$charquote *anime_character*", value = "Generates a quote from that character.")
    
  await ctx.send(embed=embed)

#@client.command()
#async def join(ctx):
#  if (ctx.author.voice):
#        channel = ctx.message.author.voice.channel
#        voice = await channel.connect()
#        #player = voice.play("audio.mp3")
#  else:
#        await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command!")

#@client.command()
#async def leave(ctx):
#  if (ctx.voice_client):
#        await ctx.guild.voice_client.disconnect()
#        await ctx.send("Peace out guys!")
#  else:
#        await ctx.send("I'm not in the voice channel.")

keep_alive()   # Keep pinging the bot so it stays awake
client.run(os.getenv('TOKEN'))   # Run the bot with the token

#https://python.land/build-discord-bot-in-python-that-plays-music
