import discord
from discord.ext import tasks
import asyncio
from urllib.parse import urlparse, parse_qs
import pickle
import os

#import the token from a file named bot_token
from bot_token import token, prefix

#dictionary syntax userid: [number of days participating, total time, dict of all dates

if os.path.exists('exported_scoreboard.pkl'):
    with open('exported_scoreboard.pkl', 'wb') as f:
        scoreboard = pickle.load(f)
        f.close()
        
else:
    scoreboard = {}

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
            for i in scoreboard:
                userid = int(i)
                print(userid)
                user = await self.fetch_user(userid)
                username = user.display_name
                print(username)
                await message.channel.send(username + ": " + str(scoreboard[i][1]))  

    @tasks.loop(seconds=60)    
    async def my_background_task(self):
        if os.path.exists('exported_scoreboard.pkl'):
            with open('exported_scoreboard.pkl', 'wb') as f:
                pickle.dump(scoreboard, f)
                f.close()
                print('exported scoreboard')

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(token)
