import hikari
import miru


class EventView(miru.View):

    @miru.button(label="Join event", style=hikari.ButtonStyle.PRIMARY)
    async def join_event(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        print("join event")
        print(button)
        print(ctx)
        await ctx.message.respond("you joined the event")