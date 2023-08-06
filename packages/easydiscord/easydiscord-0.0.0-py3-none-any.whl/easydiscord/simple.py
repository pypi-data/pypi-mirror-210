import discord 
from discord import * 
from discord.ext import commands        
from discord import app_commands



acs = discord.Client(discord.Intents.all()) 
ctxp = commands.Bot(command_prefix=P, intents=discord.Intents.all())
guilds  = discord.Object(id)

tree = app_commands.CommandTree(acs)




# user must do {whatever} = asn for quick set up, asp samthing but they will have to define p which is the prefix 

async def syncshlashid(): 
    try:        
        await tree.sync(guild=discord.Object(guilds))

        print(f' synced {acs.user.name}' )
    except Exception as e:
        print(e)
    

async def syncshlashglobal():
    try:        
        await tree.sync()

        print(f' synced {acs.user.name}' )
    except Exception as e:
        print(e)


event = '@acs.event'
slashcmdid = '@tree.command(name, description, guilds )' 
slashcmdg = '@tree.command(name, description, guilds )'


async def readyquicksetupctx(): 
    print(f'bot user: {ctxp.user.name}')
    print(f'bot id: {ctxp.user.id}')
    print(f'bot {ctxp.user.name } online')



async def readyquicksetupslash(): 
    print(f'bot user: {acs.user.name}')
    print(f'bot id: {acs.user.id}')
    print(f'bot {acs.user.name } online')
    if glidd == "true":
            syncshlashid()
        
    elif glidd == "false":
            syncshlashglobal()
        
    else:
            print("you must set glidd to true or false true meaning you are using guild id false meaning your commands are global")
            
            
            