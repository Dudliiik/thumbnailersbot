import discord
from discord.ext import commands
import asyncio
import re
from datetime import timedelta

class RqReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pattern = re.compile(r"^role-request-")
        self.required = 5
        self.delay = 3600
        self.extensions = (".png", ".jpg", ".jpeg", ".webp")
        self.poll_answers = ["Rookie Artist", "Artist-", "Artist", "Artist+", "Professional Artist"]
        self.active = set()
        self.done = set()

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.TextChannel) and self.pattern.match(channel.name):
            await asyncio.sleep(2) 
            opener = self.opener(channel)
            
            if opener:
                self.active.add(channel.id)
                self.bot.loop.create_task(self.timeout(channel, opener))

    def opener(self, channel):
        for target, overwrite in channel.overwrites.items():
            if isinstance(target, discord.Member) and overwrite.send_messages:
                return target
        return None

    async def timeout(self, channel, opener):
        await asyncio.sleep(self.delay)
        
        if channel.id in self.active and channel.id not in self.done:
            try:
                await channel.send(f"{opener.mention} Reminder to upload at least {self.required} images to start your application!")
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id not in self.active:
            return 

        has_images = any(att.filename.lower().endswith(self.extensions) for att in message.attachments)
        
        if has_images:
            total_count = 0
            async for msg in message.channel.history(limit=50):
                total_count += sum(1 for att in msg.attachments if att.filename.lower().endswith(self.extensions))

            if total_count >= self.required and message.channel.id not in self.done:
                await self.send_rq_poll(message.channel)

    async def send_rq_poll(self, channel):
        self.done.add(channel.id)
        self.active.discard(channel.id)

        poll = discord.Poll(
            question="Vote for a role",
            duration=timedelta(hours=24)
        )
        
        for answer in self.poll_answers:
            poll.add_answer(text=answer)
            
        await channel.send(poll=poll)

async def setup(bot):
    await bot.add_cog(RqReminder(bot))