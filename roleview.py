import hikari
import miru
import discord


class RoleView(miru.View):
    def __init__(self, years: dict[int, hikari.Role.id]) -> None:
        super().__init__(timeout=600)
        self.years = years
        self.select: miru.TextSelect = None

    @miru.text_select(placeholder="select the year", min_values=1, max_values=1,
                      options=[miru.SelectOption(label="placeholder")])
    async def role_select(self, select: miru.TextSelect, ctx: miru.ViewContext) -> None:
        print("role select")
        if select.values[0] == "placeholder":
            self.select = select
            options: list[hikari.SelectMenuOption] = [hikari.SelectMenuOption(
                label=str(year), description="the year you enrolled at SDU",
                value=str(self.years[year].id),
                is_default=False,
                emoji=hikari.emojis.UnicodeEmoji("📅"))
                for year in self.years.keys()]
            select.options = options
            new_select = await ctx.respond(components=self)
            await self.start(new_select)
            await ctx.respond("you activated the year role menu")
            return
        await ctx.respond(f"you selected {select.values[0]}", flags=hikari.MessageFlag.EPHEMERAL)
        print(self.years)
        await ctx.bot.rest.add_role_to_member(ctx.guild_id, ctx.author.id, int(select.values[0]))

# class TestSelect(miru.View):
#
#    @miru.text_select(
#        placeholder="Select me!",
#        options=[
#            miru.SelectOption(label="Option 1"),
#            miru.SelectOption(label="Option 2"),
#        ],
#    )
#    async def get_text(self, select: miru.TextSelect, ctx: miru.ViewContext) -> None:
#        await ctx.respond(f"You've chosen {select.values[0]}!")
#
#    @miru.user_select(placeholder="Select a user!")
#    async def get_users(self, select: miru.UserSelect, ctx: miru.ViewContext) -> None:
#        print("user select")
#        await ctx.respond(f"You've chosen {select.values[0].mention}!")
#
#    # We can control how many options should be selected
#    @miru.role_select(placeholder="Select 3-5 roles!", min_values=3, max_values=5)
#    async def get_roles(self, select: miru.RoleSelect, ctx: miru.ViewContext) -> None:
#        print("role select")
#        await ctx.respond(f"You've chosen {' '.join([role.mention for role in select.values])}!")
#
#    # A select where the user can only select text and announcement channels
#    @miru.channel_select(
#        placeholder="Select a text channel!",
#        channel_types=[
#            hikari.ChannelType.GUILD_TEXT,
#            hikari.ChannelType.GUILD_NEWS
#        ],
#    )
#    async def get_channels(self, select: miru.ChannelSelect, ctx: miru.ViewContext) -> None:
#        print("channel select")
#        await ctx.respond(f"You've chosen {select.values[0].mention}!")
#
