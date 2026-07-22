import discord
from discord.ext import commands
from config.setting import TOKEN,  BOT_PREFIX

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = BOT_PREFIX, intents = intents)

async def load_extensions():
    await bot.load_extension("cogs.music")
async def setup_hook():
    await load_extensions()
    sync = await bot.tree.sync()
    print(f'Synced {len(sync)} commands globally.')

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    sync = await bot.tree.sync()
    print(f'{bot.user} has connected to Discord!')
    print(f'guilds: {[guild.id for guild in bot.guilds]}')

    

    
bot.run(TOKEN)