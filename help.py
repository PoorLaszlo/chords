import discord
from discord.ext import commands


class Help(commands.Cog):
    """Cog for the help command."""

    def __init__(self, bot):
        self.bot = bot
        self.bot_cogs = self.bot.cogs

    @commands.command(name="help", aliases=["h"])
    async def _help(self, ctx, cog_query: str = "Music"):
        """Returns all not hidden commands from a cog.
        Default query is set to 'Music' but other cogs are supported too"""

        try:
            cog = self.bot_cogs[cog_query]
        except KeyError:
            query_error_embed = discord.Embed(
                title="Query Error. Perhaps you mean:",
                description=f"{', '.join(self.bot_cogs.keys())}.",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=query_error_embed)

        cog_help_embed = discord.Embed(
            title=f"GuraBot parancsok:",
            color=discord.Color.blue(),
        )

        for command in cog.get_commands():

            command_aliases = (
                f"{', '.join(command.aliases)}" if len(
                    command.aliases) > 0 else "None"
            )
            cog_help_embed.add_field(
                name=(f"!{command.name} , {command_aliases}") if (
                    command_aliases != "None") else (f"!{command.name}"),
                value=f"`{command.help}`",
                inline=False,
            )

        cog_help_embed.add_field(
            name="Fejlesztő:",
            value="Kókai TikTok Patrik és Gawr Gura legnagyobb rajongója lmao \U0001F525",
            inline=False
        )

        cog_help_embed.add_field(
            name="Lábjegyzet:",
            value="To do: Hamarosan jön a vicces spondzsbob parancs haha.\n(A bot nem 24/7-ben fut.) \U0001F525",
            inline=False
        )
        await ctx.send(embed=cog_help_embed)
