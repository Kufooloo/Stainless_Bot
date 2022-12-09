import discord
from discord.ext import tasks, commands
import asyncio
from urllib.parse import urlparse, parse_qs
import pickle
import os
import datetime

#import the token from a file named bot_token
from config import token, prefix, channel_id
start = datetime.datetime.now()
global scoreboard
global points
if os.path.getsize('exported_scoreboard.pkl') > 0:
    with open('exported_scoreboard.pkl', 'rb') as f:
        scoreboard = pickle.load(f)
        f.close()
if os.path.getsize('points.pkl') > 0:
    with open('points.pkl', 'rb') as f:
        points = pickle.load(f)
        f.close()
#dictionary syntax userid: [number of days participating, total time, dict of all dates]
#points dict : {user_id : points}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents, activity=discord.Game(name='Fortnite'))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(Export(bot))
    await bot.add_cog(Admin(bot))
    await bot.add_cog(Wordle(bot))


class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=['sb'])
    async def scoreboard(self, ctx):
        """Displays the scoreboard"""
        message = ""
        print("Command scoreboard detected.")
        temp = {}
        for x in scoreboard:
            temp[x] = [scoreboard[x][0], scoreboard[x][1], scoreboard[x][2]]
        print(temp)
        #print('temp')
        #print(temp)
        #print('sb')
        #print(scoreboard)
        while len(temp) != 0:
            lowest = list(temp.keys())[0]
            #print(type(lowest))
            #print(lowest)
            for i in temp:
                if temp[i][1] < temp[lowest][1]:
                    lowest = i
            userid = lowest
            #print('userid')
            #print(userid)
            user = await bot.fetch_user(userid)
            username = user.display_name
            #print('username')
            #print(username)
            average_time = scoreboard[lowest][1]/scoreboard[lowest][0]
            #await ctx.message.channel.send(username + ": " + str(scoreboard[lowest][1]) + " Average time: " + str(datetime.timedelta(seconds=average_time)))
            score = str(scoreboard[lowest][1])
            message += str(f"{username}: {score} Average Time: {str(datetime.timedelta(seconds=average_time))}\n")
            print(username + ": " + str(scoreboard[lowest][1]) + " Average time: " + str(datetime.timedelta(seconds=average_time)))
            temp.pop(lowest) 
        await ctx.message.channel.send(message)
        return
    @commands.Cog.listener()
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == bot.user.id:
            return
        print("message detected in " + str(message.channel.id))
        if message.channel.id == channel_id or message.channel.id == 653758045708615683:
            print("message in #wordle detected")
            if message.content[:5] == 'https':
                url = urlparse(message.content)
                query = parse_qs(url.query)
                date = query['d'][0]
                time = query['t'][0]
                user_id = message.author.id

                if scoreboard.get(user_id) is None:
                    scoreboard[user_id] = [1, int(time), {date:time}]
                else:
                    user_list = scoreboard[user_id]
                    user_list[0] += 1
                    user_list[1] += int(time)
                    user_list[2].update({date:time})


                await message.reply('Date: ' + date + ' Time: ' + time, mention_author=True)
                return
        else:
            user_id = message.author.id
            if points.get(user_id) is None:
                points[user_id] = 1
            else:
                points[user_id] += 1
                user = await bot.fetch_user(user_id)
                username = user.display_name
                print("added point to " + username + " new point total: " + str(points[user_id]))
                return              

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

class Export(commands.Cog):
    def __init__(self, bot1):
        self.bot = bot1
        self.export.start()

    def cog_unload(self):
        with open('exported_scoreboard.pkl', 'wb') as f:
            pickle.dump(scoreboard, f)
            f.close()
            print('exported scoreboard')
            print(scoreboard)
        with open('points.pkl', 'wb') as f:
            pickle.dump(points, f)
            f.close()
            print('exported points')
            print(points)
        self.export.cancel()

    @tasks.loop(seconds=60)
    async def export(self):
    #every 60s exports the scoreboard
        if os.path.exists('exported_scoreboard.pkl'):
            with open('exported_scoreboard.pkl', 'wb') as f:
                pickle.dump(scoreboard, f)
                f.close()
                print('exported scoreboard')
                print(scoreboard)
        if os.path.exists('points.pkl'):
            with open('points.pkl', 'wb') as f:
                pickle.dump(points, f)
                f.close()
                print('exported points')
                print(points)
    @export.before_loop
    async def before_my_task(self):
    #loads the scoreboard from the .pkl file
        if os.path.exists('exported_scoreboard.pkl'):
            if os.path.getsize('exported_scoreboard.pkl') > 0:
                print("file is larger than 0")
                with open('exported_scoreboard.pkl', 'rb') as f:
                    scoreboard = pickle.load(f)
                    f.close()
        if os.path.exists('points.pkl'):
            if os.path.getsize('points.pkl') > 0:
                print("file is larger than 0")
                with open('points.pkl', 'rb') as f:
                    scoreboard = pickle.load(f)
                    f.close()

bot.run(token)
