import os
import time
import random
import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks

MY_ID = 1337973255977570345
APPLICATION_ID = xx

banned_users = set()
muted_users = {}
ping_history = {}

# self_bot=True alone often ignores commands from other users.
# Public commands are handled manually in on_message instead.
bot = commands.Bot(command_prefix='.', self_bot=True, help_command=None)


def is_me():
    def predicate(ctx):
        return ctx.author.id == MY_ID
    return commands.check(predicate)


async def reply_msg(message, content: str):
    """Reply or send — works for any author."""
    try:
        await message.reply(content, mention_author=False)
    except Exception:
        try:
            await message.channel.send(content)
        except Exception as e:
            print(f"reply failed: {e}")


async def reply_edit_or_send(message, content: str):
    """If you wrote the command → edit. Anyone else → reply."""
    if message.author.id == bot.user.id:
        try:
            await message.edit(content=content)
            return
        except Exception:
            pass
    await reply_msg(message, content)


# ── Presence (buttons only visible to OTHER people, never yourself) ─────────

@tasks.loop(minutes=5)
async def keep_presence_alive():
    try:
        # Preferred API (discord.py-self >= 2.1)
        buttons = [
            discord.ActivityButton("dc", "https://discord.gg/36EAyW5Z4F"),
            discord.ActivityButton("guns", "https://guns.lol/tpa"),
        ]
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name=".gg/36EAyW5Z4F",
            details="Read Bio",
            state="Germany",
            application_id=APPLICATION_ID,
            buttons=buttons,
        )
        await bot.change_presence(status=discord.Status.dnd, activity=activity)
        print("Presence updated (ActivityButton).")
    except Exception as e:
        print(f"Presence ActivityButton failed: {e} — trying fallback")
        try:
            # Fallback: labels + urls as dicts (some builds accept this)
            activity = discord.Activity(
                type=discord.ActivityType.playing,
                name=".gg/36EAyW5Z4F",
                details="Read Bio",
                state="Germany",
                application_id=APPLICATION_ID,
                buttons=[
                    {"label": "dc", "url": "https://discord.gg/36EAyW5Z4F"},
                    {"label": "guns", "url": "https://guns.lol/tpa"},
                ],
            )
            await bot.change_presence(status=discord.Status.dnd, activity=activity)
            print("Presence updated (dict fallback).")
        except Exception as e2:
            print(f"Presence fallback failed: {e2}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    if not keep_presence_alive.is_running():
        keep_presence_alive.start()
    # Set once immediately
    await keep_presence_alive()
    print("Rich Presence loop started.")


# ── Owner-only commands (still via command framework) ───────────────────────

@bot.command()
@is_me()
async def ban(ctx, user: discord.User):
    banned_users.add(user.id)
    await reply_edit_or_send(ctx.message, f"🚫 Banned **{user.name}** from auto-responder.")


@bot.command()
@is_me()
async def unban(ctx, user: discord.User):
    if user.id in banned_users:
        banned_users.remove(user.id)
        await reply_edit_or_send(ctx.message, f"✅ Unbanned **{user.name}**.")
    else:
        await reply_edit_or_send(ctx.message, f"⚠️ **{user.name}** is not banned.")


@bot.command()
@is_me()
async def server(ctx, source_id: int):
    target = ctx.guild
    if target is None:
        await reply_edit_or_send(ctx.message, "❌ Use this inside a server.")
        return

    source = bot.get_guild(source_id)
    if source is None:
        await reply_edit_or_send(ctx.message, "❌ Source server not found (you must be in both).")
        return

    await reply_edit_or_send(
        ctx.message,
        f"⏳ Cloning **{source.name}** → **{target.name}** ... this can take a while."
    )

    role_map = {}
    created_roles = 0
    created_channels = 0

    try:
        roles = sorted(
            [r for r in source.roles if r.name != "@everyone"],
            key=lambda r: r.position
        )
        for role in roles:
            try:
                new_role = await target.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                    reason="Server clone",
                )
                role_map[role.id] = new_role
                created_roles += 1
                await asyncio.sleep(0.8)
            except Exception as e:
                print(f"Role fail {role.name}: {e}")

        cat_map = {}
        for cat in sorted(source.categories, key=lambda c: c.position):
            try:
                overwrites = {}
                for obj, ow in cat.overwrites.items():
                    if isinstance(obj, discord.Role) and obj.id in role_map:
                        overwrites[role_map[obj.id]] = ow
                    elif isinstance(obj, discord.Role) and obj.name == "@everyone":
                        overwrites[target.default_role] = ow
                new_cat = await target.create_category(
                    name=cat.name,
                    overwrites=overwrites or None,
                    reason="Server clone",
                )
                cat_map[cat.id] = new_cat
                created_channels += 1
                await asyncio.sleep(0.8)
            except Exception as e:
                print(f"Category fail {cat.name}: {e}")

        channels = sorted(
            [c for c in source.channels if not isinstance(c, discord.CategoryChannel)],
            key=lambda c: c.position,
        )
        for ch in channels:
            try:
                overwrites = {}
                for obj, ow in ch.overwrites.items():
                    if isinstance(obj, discord.Role) and obj.id in role_map:
                        overwrites[role_map[obj.id]] = ow
                    elif isinstance(obj, discord.Role) and obj.name == "@everyone":
                        overwrites[target.default_role] = ow
                parent = cat_map.get(ch.category_id) if ch.category_id else None

                if isinstance(ch, discord.TextChannel):
                    await target.create_text_channel(
                        name=ch.name,
                        topic=ch.topic,
                        slowmode_delay=ch.slowmode_delay,
                        nsfw=ch.nsfw,
                        category=parent,
                        overwrites=overwrites or None,
                        reason="Server clone",
                    )
                elif isinstance(ch, discord.VoiceChannel):
                    await target.create_voice_channel(
                        name=ch.name,
                        bitrate=min(ch.bitrate, target.bitrate_limit),
                        user_limit=ch.user_limit,
                        category=parent,
                        overwrites=overwrites or None,
                        reason="Server clone",
                    )
                created_channels += 1
                await asyncio.sleep(0.8)
            except Exception as e:
                print(f"Channel fail {ch.name}: {e}")

        await reply_edit_or_send(
            ctx.message,
            f"✅ Clone done!\nRoles: **{created_roles}**\nChannels/Cats: **{created_channels}**\n"
            f"`{source.name}` → `{target.name}`",
        )
    except Exception as e:
        await reply_edit_or_send(ctx.message, f"❌ Clone failed: `{e}`")


# ── Public command handlers (ANY user) ──────────────────────────────────────

async def handle_public(message):
    content = (message.content or "").strip()
    if not content.startswith("."):
        return False

    # normalize: .ping / .PING / . ping
    parts = content[1:].split(maxsplit=1)
    if not parts:
        return False
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in ("cmd", "commands", "help"):
        await reply_edit_or_send(message, (
            "**Commands**\n"
            "`.ping` – Latency\n"
            "`.donate` – Crypto addresses\n"
            "`.cat` – Random cat image\n"
            "`.quote` / `.qoute` – Random quote\n"
            "`.joke` – Random joke\n"
            "`.rate [@user]` – Cuteness 0-100\n"
            "`.cmd` – This list\n\n"
            "**Owner only**\n"
            "`.ban @user` / `.unban @user`\n"
            "`.server <source_id>` – Clone roles & channels"
        ))
        return True

    if cmd == "ping":
        latency = round(bot.latency * 1000)
        await reply_edit_or_send(message, f"🏓 Pong! Latency: `{latency}ms`")
        return True

    if cmd == "donate":
        await reply_edit_or_send(message, (
            "**Donate**\n"
            "Litecoin: `LSC6QoQ9MsQ4C9U2QbVCjh82xC1TCTmRo8`\n"
            "Bitcoin: `bc1qw8flzl8jgug7eqng5xp8zzv94ylpmnpf6v7g25`\n\n"
            "Thanks for any amount of donate!"
        ))
        return True

    if cmd == "cat":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                    if resp.status != 200:
                        await reply_edit_or_send(message, "😿 Couldn't fetch a cat right now.")
                        return True
                    data = await resp.json()
                    url = data[0]["url"]
            await reply_edit_or_send(message, url)
        except Exception:
            await reply_edit_or_send(message, "😿 Something went wrong while fetching a cat.")
        return True

    if cmd in ("quote", "qoute"):
        urls = [
            "https://zenquotes.io/api/random",
            "https://api.quotable.io/random",
        ]
        try:
            async with aiohttp.ClientSession() as session:
                for url in urls:
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                            if resp.status != 200:
                                continue
                            data = await resp.json()
                            if isinstance(data, list) and data:
                                text = data[0].get("q", "")
                                author = data[0].get("a", "Unknown")
                            else:
                                text = data.get("content", "")
                                author = data.get("author", "Unknown")
                            if text:
                                await reply_edit_or_send(message, f'💭 "{text}"\n— **{author}**')
                                return True
                    except Exception:
                        continue
            await reply_edit_or_send(message, "❌ Couldn't fetch a quote right now.")
        except Exception:
            await reply_edit_or_send(message, "❌ Something went wrong while fetching a quote.")
        return True

    if cmd == "joke":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
                    if resp.status != 200:
                        await reply_edit_or_send(message, "❌ Couldn't fetch a joke.")
                        return True
                    data = await resp.json()
                    setup = data.get("setup", "")
                    punchline = data.get("punchline", "")
            await reply_edit_or_send(message, f"😂 **{setup}**\n\n||{punchline}||")
        except Exception:
            await reply_edit_or_send(message, "❌ Something went wrong while fetching a joke.")
        return True

    if cmd == "rate":
        score = random.randint(0, 100)
        target = "you"
        if message.mentions:
            target = message.mentions[0].mention
        elif arg.strip():
            target = arg.strip()
        if score >= 90:
            comment = "extremely cute 💖"
        elif score >= 70:
            comment = "very cute 🥰"
        elif score >= 50:
            comment = "pretty cute 😊"
        elif score >= 30:
            comment = "kinda cute 🤔"
        else:
            comment = "needs more cuteness 😢"
        await reply_edit_or_send(
            message,
            f"✨ Cuteness rating for {target}: **{score}/100** — {comment}",
        )
        return True

    return False


@bot.event
async def on_message(message):
    # 1) Public commands from ANYONE (including you)
    try:
        handled = await handle_public(message)
        if handled:
            return
    except Exception as e:
        print(f"public cmd error: {e}")

    # 2) Owner commands (.ban / .unban / .server)
    await bot.process_commands(message)

    # 3) Auto-responder on mention (not for own messages / banned)
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
            del muted_users[user_id]

        if user_id not in ping_history:
            ping_history[user_id] = []
        ping_history[user_id].append(now)
        ping_history[user_id] = [t for t in ping_history[user_id] if now - t <= 10]

        if len(ping_history[user_id]) >= 3:
            muted_users[user_id] = now + 30
            try:
                await message.reply(
                    "You are spamming. The auto-responder is ignoring you for 30 seconds.",
                    mention_author=False,
                )
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
        print("ERROR: DISCORD_TOKEN is missing.")
        exit(1)
    bot.run(token)
