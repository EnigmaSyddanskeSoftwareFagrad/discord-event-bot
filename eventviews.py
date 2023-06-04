import hikari
import miru


class EventView(miru.View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.attendees = []
        self.buttons = {}

    @miru.button(label="Join event", style=hikari.ButtonStyle.PRIMARY)
    async def join_event(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if self.buttons.get("join evnent") is None:
            self.buttons["join event"] = button
        print("join event")
        print(button)
        print(ctx)
        if ctx.member.id not in self.attendees:
            self.attendees.append(ctx.member.id)
            button.label = f'Join event: Attendees ({len(self.attendees)})'
            await ctx.edit_response(components=self)
            await ctx.respond("you joined the event", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await ctx.respond("you already joined the event", flags=hikari.MessageFlag.EPHEMERAL)

    @miru.button(label="Leave event", style=hikari.ButtonStyle.DANGER)
    async def leave_event(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        if self.buttons.get("leave event") is None:
            self.buttons["leave event"] = button
        print("leave event")
        print(button)
        print(ctx)
        if ctx.member.id in self.attendees:
            self.attendees.remove(ctx.member.id)
            self.buttons["join event"].label = f'Join event: Attendees ({len(self.attendees)})'
            await ctx.edit_response(components=self)
            await ctx.respond("you left the event", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await ctx.respond("you're not signed up for the event", flags=hikari.MessageFlag.EPHEMERAL)