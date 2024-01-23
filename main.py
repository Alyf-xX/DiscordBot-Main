import os
import asyncio
import discord
from discord.ext import commands
import aiohttp
from fastapi import FastAPI
import uvicorn

app = FastAPI()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!', '<@bot_id>'),
    intents=intents
)

report_channel_id = 1198943452616982699

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

async def shorten_url(original_url, length):
    length = max(5, min(length, 30))
    api_url = f'https://mizikai.ink/api/?url={original_url}&length={length}'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            data = await response.json()
            return data.get('shorten')

@app.get("/")
async def read_root():
    return {"message": "Bot is online!"}

@bot.command(name='short', help='Shorten a URL.')
async def shorten_command(ctx, url, length: int = 10, embed_response: bool = False):
    try:
        length = max(5, min(length, 30))
        short_url = await shorten_url(url, length)
        if short_url:
            if embed_response:
                embed = discord.Embed(
                    title='Shortened URL',
                    description=f'Original URL: {url}\nLength: {length} characters\nShortened URL: {short_url}',
                    color=discord.Color.blue()
                )
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(f'Original URL: ```{url}```\nLength: {length} characters\nShortened URL: {short_url}')
                report_channel = bot.get_channel(report_channel_id)
                if report_channel:
                    await report_channel.send(f'ユーザー {ctx.author.mention} が `/short` コマンドを使用しました。\n```{ctx.message.content}```')
                else:
                    await ctx.reply('Failed to shorten the URL. Please check the provided URL.')
    except Exception as e:
        await ctx.reply(f'Error shortening URL: {e}')

@bot.command(name='today', help='Display the current date and time.')
async def today(ctx):
    current_time = discord.utils.utcnow()
    await ctx.send(f'Today is {current_time.strftime("%Y-%m-%d %H:%M:%S")} UTC')

@bot.command(name='list', help='Display the list of available commands.')
async def show_command_list(ctx):
    command_list = [command.name for command in bot.commands]
    await ctx.send(f'ドキュメント(コマンド等も記載しています)\nhttps://link.lapius-cards.pro/Lapius-DIscordBot')

@bot.command(name='adminhelp', help='Send admin help message to a specific channel.')
async def admin_help(ctx, title, text):
    try:
        sender_mention = f'<@{ctx.author.id}>'
        message_content = f'送信者: {sender_mention}\nタイトル: {title}\n本文: {text}'
        target_channel_id = 1198628540371968020
        target_channel = bot.get_channel(target_channel_id)

        if target_channel:
            sent_message = await target_channel.send(message_content)
            await ctx.reply(
                f'メッセージが送信されました。サポーターによるお問い合わせ内容の確認の上でご返信させていただきますのでいましばらくお待ちください。\n---\n{sent_message.content}'
            )
        else:
            await ctx.reply('指定されたチャンネルが見つかりませんでした.')
    except Exception as e:
        await ctx.reply(f'エラーが発生しました: {e}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `/list` to display the list of commands.")


TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
