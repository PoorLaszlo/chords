from help import Help
from music import Music
import keep_alive
import os
import discord
from discord.ext import commands

#from dotenv import load_dotenv
#load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")
with open('prefix.txt', 'r') as fp:
    prefix = fp.read()

activity = discord.Game(name="!help for Jason Momoa COOM")
bot = commands.Bot(command_prefix=prefix, intents=intents, activity=activity, status=discord.Status.idle)
bot.remove_command('help')
bot.add_cog(Music(bot))
bot.add_cog(Help(bot))
keep_alive.keep_alive()
bot.run(os.getenv("TOKEN"))
