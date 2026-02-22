import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Blacklist
BLACKLIST = {"shit", "damn", "bitch"}
warned_users = set()


@bot.event
async def on_ready():
    print(f"Bot online: {bot.user.name}")

@bot.event
async def on_member_join(member):
    try:
        # DM welcome
        await member.send(f"Welcome to the server, {member.name}!")
    except Exception:
        print(f"Unable to send DM to {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Filter offensive words with reply
    if any(word in message.content.lower() for word in BLACKLIST):
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print(f"No permission to delete message from {message.author}")
        if message.author.id not in warned_users:
            await message.reply("Please do not use offensive words!", mention_author=True)
            warned_users.add(message.author.id)

    await bot.process_commands(message)


@bot.command()
async def ping(ctx):
    await ctx.reply("Pong!", mention_author=True)

@bot.command()
async def hello(ctx):
    await ctx.reply(f"Hello {ctx.author.mention}!", mention_author=True)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.reply(f"Role '{role_name}' not found.", mention_author=True)
        return
    if role >= ctx.guild.me.top_role:
        await ctx.reply("I can't assign a role higher or equal to my top role!", mention_author=True)
        return
    try:
        await member.add_roles(role)
        await ctx.reply(f"{member.mention} has been given the role {role.name}!", mention_author=True)
    except discord.Forbidden:
        await ctx.reply("I don't have permission to manage this role.", mention_author=True)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.reply(f"Role '{role_name}' not found.", mention_author=True)
        return
    try:
        await member.remove_roles(role)
        await ctx.reply(f"{member.mention} had the role {role.name} removed.", mention_author=True)
    except discord.Forbidden:
        await ctx.reply("I don't have permission to manage this role.", mention_author=True)


@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.reply("You need at least 2 options for a poll!", mention_author=True)
        return

    if len(options) > 10:
        await ctx.reply("Maximum 10 options allowed!", mention_author=True)
        return

    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    description = ""
    for i, option in enumerate(options):
        description += f"{emojis[i]} {option}\n"
    embed.add_field(name="Options", value=description, inline=False)
    poll_message = await ctx.send(embed=embed)

    # Add reactions
    for i in range(len(options)):
        await poll_message.add_reaction(emojis[i])


bot.run(token, log_handler=handler, log_level=logging.DEBUG)