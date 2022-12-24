import discord
from discord.ext import tasks, commands
import asyncio
from urllib.parse import urlsplit, parse_qs
import pickle
import os
import datetime
import pandas as pd
import math

#local imports
from config import token, prefix, channel_id
from Classes import Server, User, Day

start = datetime.datetime.now()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents, activity=discord.Game(name='Fortnite'))


#---------------------------------------------------
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(Wordle(bot))
    await bot.add_cog(Admin(bot))

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.export.start()

    @commands.command(aliases=['sb'])
    async def scoreboard(self, ctx):
        """Displays the scoreboard"""
        message = ""
        score_list = self.server.get_scoreboard()
        print(score_list)
        key_list = list(score_list.keys())
        key_list.sort()
        print(key_list)
        for key in key_list:
            userid = score_list[key]
            user = await bot.fetch_user(userid)
            avg_time = self.server.get_avg_time(userid)
            math.floor(avg_time)
            avg_time_dt = datetime.timedelta(seconds=avg_time)
            avg_time_str = str(avg_time_dt - datetime.timedelta(microseconds=avg_time_dt.microseconds))
            message += f"{user.display_name} has a score of {round(key, 2)} with an average time of {avg_time_str}\n"
        await ctx.message.channel.send(message)
        return
    @commands.command()
    async def score(self, ctx, member: discord.Member):
        """Gives the score as well as other information on given user\n score @(user)"""
        userid = member.id
        print(f"{userid}'s score was requested by {ctx.message.author.display_name}")
        user = await bot.fetch_user(userid)
        display_name = user.display_name
        avg_time = self.server.get_avg_time(userid)
        math.floor(avg_time)
        avg_time_str = str(datetime.timedelta(seconds=avg_time))
        message = f"{display_name} has an average time of {avg_time_str}.\n"
        message += self.server.user_score(userid)
        await ctx.message.channel.send(message)
        return
    @commands.Cog.listener()
    async def on_message(self, message):
        global most_recent_date
        # we do not want the bot to reply to itself
        if message.author.id == bot.user.id:
            return
        print("message detected in " + str(message.channel.id))
        if message.channel.id == channel_id or message.channel.id == 653758045708615683:
            print("message in #wordle detected")
            if message.content[:5] == 'https':
                url = urlsplit(message.content)
                if url.netloc != "www.nytimes.com":
                    await message.reply("This is not a Crossword link dumbass")
                    return
                query = parse_qs(url.query)
                date = query['d'][0]
                time = query['t'][0]
                userid = message.author.id
                self.server.add_score(userid, date, time)
                await message.reply('Date: ' + date + ' Time: ' + time, mention_author=True)
                return

    @tasks.loop(seconds=60)
    async def export(self):
        """exports the scoreboard and points dict"""
        #every 60s exports the scoreboard
        with open('Server_Class.pkl', 'wb') as f:
            pickle.dump(self.server, f)
            f.close
            print("Exported Server")
    @export.before_loop
    async def before_my_task(self):
        """before starting the task open the dicts"""
        #loads the scoreboard from the .pkl file
        if os.path.exists('Server_Class.pkl'):
            with open('Server_Class.pkl', 'rb') as f:
                self.server = pickle.load(f)
                f.close()
                print("Loaded Scoreboard")
                return
        self.server = Server()
        return
    @commands.command(hidden=True)
    @commands.is_owner()
    async def transfer(self, ctx, name:str):
        if os.path.exists(name):
            with open(name, 'rb') as f:
                scoreboard_import = pickle.load(f)
                f.close()
                await ctx.message.channel.send(f"Opened file {name} with contents {scoreboard_import}")
            for userid, contents in scoreboard_import.items():
                user = await bot.fetch_user(userid)
                display_name = user.display_name
                message =  f"Found user: {display_name} Id: {userid}\n"
                message += f"They have participated for {contents[0]} days and have a total time of {contents[1]}\n"
                message += "Beggining import process"
                await ctx.message.channel.send(message)
                days = contents[2]
                key_list = list(days.keys())
                for key in key_list:
                    date = key
                    time = int(days.get(key))
                    self.server.add_score(userid, date, time)
                    await ctx.message.channel.send(f"Added date: {date} with time {time}")
                self.server.get_score(userid)
        else:
            await ctx.message.channel.send(f"Failed to locate file {name}")


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(hidden=True)
    @commands.is_owner()
    async def kill(self, ctx):
        """Kills the program"""
        await bot.remove_cog('Export')
        await bot.close()

    @commands.command()
    async def uptime(self, ctx):
        """Displays how long the bot has been running"""
        now = datetime.datetime.now()
        diffrence = now - start
        await ctx.message.channel.send("Running for: " + str(diffrence))
        return

bot.run(token)