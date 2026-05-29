import discord
from discord import app_commands
from main import owner_or_permissions
from datetime import timedelta
import re
import asyncio

# ---------------------------------------------

class Roles(app_commands.Group):
    def __init__(self):
        super().__init__(name="role", description="Role commands")

    @app_commands.command(
        name="add",
        description="Adds a role to a member.",
    )
    @owner_or_permissions(manage_roles=True)
    async def addRole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        await interaction.response.defer()
        try:
            if role >= interaction.guild.me.top_role:
                await interaction.followup.send("I cannot assign this role because it is higher than my highest role!")
                return

            if role in user.roles:
                await interaction.followup.send(f"{user.name} already has the role {role.name}")
            else:
                await user.add_roles(role)
                await interaction.followup.send(f"Added {role.name} to {user.name}!")
        except discord.Forbidden:
            await interaction.followup.send(f"I cannot manage the role {role.name}")

# ---------------------------------------------

    @app_commands.command(
        name="remove",
        description="Removes a role from a member.",
    )
    @owner_or_permissions(manage_roles=True)
    async def removeRole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        await interaction.response.defer()
        try:
            if role >= interaction.guild.me.top_role:
                await interaction.followup.send("I cannot remove this role because it is higher than my highest role!")
                return
                
            if role not in user.roles:
                 await interaction.followup.send(f"{user.name} doesn't have this role")
            else:
                 await user.remove_roles(role)
                 await interaction.followup.send(f"Removed {role.name} from {user.name}!")
        except discord.Forbidden:
            await interaction.followup.send(f"I cannot manage the role {role.name}")

# ---------------------------------------------

@app_commands.command(
    name="clear",
    description="Clears messages",
)
@owner_or_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer()
    deleted = await interaction.channel.purge(limit=amount+1)
    real_deleted = max(len(deleted) - 1, 0)
    await interaction.channel.send(f"Cleared {real_deleted} messages", delete_after=4)

# ---------------------------------------------

@app_commands.command(
    name="artistpoll",
    description="Posts an artist vote poll (optional)",
)
@owner_or_permissions(administrator=True)
async def artistpoll(interaction: discord.Interaction):
    poll = discord.Poll(question="Vote for an artist role", duration=timedelta(hours=24))

    poll.add_answer(text="Rookie Artist")
    poll.add_answer(text="Artist-")
    poll.add_answer(text="Artist")
    poll.add_answer(text="Artist+")
    poll.add_answer(text="Professional Artist")

    await interaction.response.send_message(poll=poll)

# ---------------------------------------------

@app_commands.command(
    name="kick",
    description="Kick a member.",
)
@owner_or_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member):
    await member.kick(reason=f"Kicked by {interaction.user}.")
    await interaction.response.send_message(f"{member.mention} was kicked.")

# ---------------------------------------------

@app_commands.command(name="ban", description="Ban a member.")
@owner_or_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, duration: str = None, delete_messages: bool = False, reason: str | None = None):
    await interaction.response.defer()
    await member.ban(reason=reason, delete_message_days=(7 if delete_messages else 0))

    s = 0
    if duration:
        m = re.fullmatch(r"(\d+)([smhd])", duration.lower())
        if m:
            number, unit = int(m[1]), m[2]
            s = number * {'s':1, 'm':60, 'h':3600, 'd':86400}[unit]

    embed = discord.Embed(
        title="Banned Successfully",
        description=(f"{member.mention} has been banned\nDuration: {duration or 'Permanent'}\nReason: **{reason or 'No reason provided'}**"),
        color=discord.Color.red()
    )

    await interaction.followup.send(embed=embed)

    if s > 0:
        await asyncio.sleep(s)
        try:
            await interaction.guild.unban(discord.Object(id=member.id))
        except discord.NotFound:
            pass
# ---------------------------------------------

@app_commands.command(
    name="unban",
    description="Unban a member.",
)
@owner_or_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user: str, reason: str = None):
    await interaction.response.defer() 
    
    try:
        user_id_int = int(user)
        user_obj = await interaction.client.fetch_user(user_id_int)
        await interaction.guild.unban(user_obj, reason=reason)

        embed = discord.Embed(
            title="Unban successfully",
            description=f"**{user_obj.name}** has been unbanned.\nReason: {reason}",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed) 
    except Exception as e:
        await interaction.followup.send(f"User already unbanned.")

# ---------------------------------------------

async def setup(bot):
    bot.tree.add_command(Roles())
    bot.tree.add_command(clear)
    bot.tree.add_command(artistpoll)
    bot.tree.add_command(kick)
    bot.tree.add_command(ban)
    bot.tree.add_command(unban)