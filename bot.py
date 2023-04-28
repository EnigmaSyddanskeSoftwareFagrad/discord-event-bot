import json
import string
import hikari
import lightbulb
import confmanager


disc_values = confmanager.confmanager()
bot = lightbulb.BotApp(token=disc_values.get_token())


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    """If a non-bot user mentions your bot, respond with 'Pong!'."""
    if not event.is_human:
        return

    me = bot.get_me()

    if me.id in event.message.user_mentions_ids:
        await event.message.respond("Pong!")


# Enigma role has id 1101493726632738826
@bot.command
@lightbulb.add_checks(lightbulb.has_roles(disc_values.get_enigma_role_id()))
@lightbulb.option("event_name", "Name of the event", str)
@lightbulb.option("event_link", "Link to facebook event", str)
@lightbulb.command('addevent', 'sends pong')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.SlashContext):
    event_channel = disc_values.get_event_channel()
    await bot.rest.create_message(event_channel, f"**{ctx.options.event_name}**\n{ctx.options.event_link}")
    await ctx.author.send("Thank you for using \"Enigma Event Bot\"! Your event will be added shortly, please provide"
                          " a description in the next message, prefixed with: \n\n @Enigma-event-bot#1500 description:")
    await ctx.respond(ctx.options.event_name)


if __name__ == '__main__':
    bot.run()
