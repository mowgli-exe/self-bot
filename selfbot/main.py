import os
import time
import discord
from discord.ext import commands, tasks

MY_ID = YOURE_DISCORD_ID
APPLICATION_ID = 676767

banned_users = set()
muted_users = {}
ping_history = {}

bot = commands.Bot(command_prefix='.', self_bot=True, help_command=None)

def is_me():
    def predicate(ctx):
        return ctx.author.id == MY_ID
    return commands.check(predicate)

# This loop ensures Discord doesn't drop your status after a few minutes
@tasks.loop(minutes=5)
async def keep_presence_alive():
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="love her.",
        details="I love sleeping",
        state="sleeping",
        application_id=APPLICATION_ID, 
        buttons=[
            {"label": "discord", "url": "https://discord.gg/36EAyW5Z4F"}
        ]
    )
    # Forced status to Do Not Disturb to override your desktop client's status
    await bot.change_presence(status=discord.Status.dnd, activity=activity)

@bot.event
async def on_ready():
    print(f"Logged in successfully as {bot.user} (ID: {bot.user.id})")
    
    # Start the loop if it isn't already running
    if not keep_presence_alive.is_running():
        keep_presence_alive.start()
        
    print("Rich Presence loop initialized.")

@bot.command()
@is_me()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.message.edit(content=f"🏓 Pong! Latency: `{latency}ms`")

@bot.command()
@is_me()
async def ban(ctx, user: discord.User):
    banned_users.add(user.id)
    await ctx.message.edit(content=f"🚫 Banned **{user.name}** from triggering the auto-responder.")

@bot.command()
@is_me()
async def unban(ctx, user: discord.User):
    if user.id in banned_users:
        banned_users.remove(user.id)
        await ctx.message.edit(content=f"✅ Unbanned **{user.name}**.")
    else:
        await ctx.message.edit(content=f"⚠️ **{user.name}** is not banned.")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.id == bot.user.id:
        return

    if message.author.id in banned_users:
        return

    if bot.user.mentioned_in(message):
        now = time.time()
        user_id = message.author.id

        if user_id in muted_users:
            if now < muted_users[user_id]:
                return  
            else:
                del muted_users[user_id]  

        if user_id not in ping_history:
            ping_history[user_id] = []
        
        ping_history[user_id].append(now)
        ping_history[user_id] = [t for t in ping_history[user_id] if now - t <= 10]

        if len(ping_history[user_id]) >= 3:
            muted_users[user_id] = now + 30 
            try:
                await message.reply("You are spamming. The auto-responder is ignoring you for 30 seconds.", mention_author=False)
            except discord.HTTPException:
                pass
            return

        try:
            await message.reply("this user is not awake, try it later.", mention_author=False)
        except discord.HTTPException:
            pass

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN variable is missing from environment variables.")
        exit(1)
        
    bot.run(token)
