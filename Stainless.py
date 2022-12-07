import discord
from discord.ext import tasks
import asyncio
from urllib.parse import urlparse, parse_qs
import pickle
import os
import datetime

#import the token from a file named bot_token
from bot_token import token, prefix, channel_id
scoreboard = {}
points = {}
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




class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------') 

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_message(self, message):
       # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return     
        print("message detected in " + str(message.channel.id))
        if message.channel.id == channel_id:
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
            if message.content.startswith(prefix+'sb'):
                temp = {}
                for x in scoreboard:
                    temp[x] = [scoreboard[x][0], scoreboard[x][1], scoreboard[x][2]]
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
                    user = await self.fetch_user(userid)
                    username = user.display_name
                    #print('username')
                    #print(username)
                    average_time = scoreboard[lowest][1]/scoreboard[lowest][0]
                    await message.channel.send(username + ": " + str(scoreboard[lowest][1]) + " Average time: " + str(datetime.timedelta(seconds=average_time)))
                    temp.pop(lowest)
        else: 
            user_id = message.author.id
            if points.get(user_id) is None:
                points[user_id] = 1
            else:
                points[user_id] += 1

    @tasks.loop(seconds=60)    
    async def my_background_task(self):
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

    @my_background_task.before_loop
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
        await self.wait_until_ready()  # wait until the bot logs in

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(token)
client = discord.Client(activity=discord.Game(name='Fortnite'))
