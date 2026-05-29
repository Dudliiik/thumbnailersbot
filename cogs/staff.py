import discord
from discord import app_commands

STAFF_ROLES = {
    "Owner": 1102968475300937801,
    "Co-owner": 1102974477580648478,
    "Admin": 1102975816062730291,
    "Mod": 1102976554759368818,
    "Developer": 1417210748907687997,
    "Helper": 1135500243446808587
}

@app_commands.command(name="staff", description="Lists all staff members.")
async def staff(interaction: discord.Interaction):
    guild = interaction.guild
    all_members = guild.members

    staff_roles = []
    for name, rid in STAFF_ROLES.items():
        role = guild.get_role(rid)
        if role:
            staff_roles.append((name, role))

    staff_roles.sort(key=lambda r: r[1].position, reverse=True)
    
    listed_members = set()
    embed_description = ""

    for role_name, role in staff_roles:
        embed_description += f"**{role_name}:**\n"

        members_in_role = []
        for member in role.members:
            if member.id not in listed_members:
                listed_members.add(member.id)
                members_in_role.append(f"> - <@{member.id}>")

        if members_in_role:
            embed_description += "\n".join(members_in_role) + "\n"
        else:
            embed_description += "*No members*\n"

        embed_description += "\n"

    staff_embed = discord.Embed(
        title="Thumbnailers Staff",
        description=embed_description[:4096],
        color=discord.Color.dark_blue()
    )

    await interaction.response.send_message(embed=staff_embed, allowed_mentions=discord.AllowedMentions(users=True, roles=True))

async def setup(bot):
    bot.tree.add_command(staff)