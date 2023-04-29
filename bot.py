import re
import hikari
from hikari.events import message_events
import lightbulb
import confmanager
import eventcreator
from eventcreator import Event

disc_values = confmanager.ConfManager()
bot = lightbulb.BotApp(token=disc_values.token)


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human:
        return

    me = bot.get_me()
    if me is None:
        return
    if not event.message.user_mentions_ids:
        return

    if me.id in event.message.user_mentions_ids:
        await event.message.respond("Pong!")


@bot.listen()
async def on_event_description(event: message_events.DMMessageCreateEvent) -> None:
    if not event.is_human:
        return
    message = event.message
    print("on event description")
    print(message.content)
    if message.content is None:
        return
    if message.content.startswith(f'<@{disc_values.bot_id}> name:'):
        pattern = re.compile(r"^<@\d+> name:(?P<event_name>.*?) description:")
        match = pattern.match(message.content)
        if match:
            event_name = match.group("event_name")
            description = message.content.replace(f"<@{disc_values.bot_id}> name:{event_name} description:", "")
            eventcreator.set_event_description(event_name, message.author.id, description)
            await message.author.send("Thank you for using \"Enigma Event Bot\"! "
                                            "Your event will be added shortly...")
            new_event: Event = eventcreator.get_event(event_name, message.author.id)
            print("event name", new_event.event_name)

            await message.author.send("your event will be representated like this:\n")
            await message.author.send(new_event)
            await message.author.send("If you want to change the description of your event"
                                            " repeat your last message with the new description.\n\n"
                                            "if you want to post your event send:\n"
                                            f"@Enigma-event-bot#1500 post name:{event_name}")
        else:
            await message.author.send("sorry I couldn't extract the name of the event")

@bot.listen()
async def on_event_post(event: message_events.DMMessageCreateEvent) -> None:
    if not event.is_human:
        return
    message = event.message
    print("on event post")
    print(message.content)
    if message.content is None:
        return
    if message.content.startswith(f'<@{disc_values.bot_id}> post name:'):
        pattern = re.compile(r"^<@\d+> post name:\s*(?P<event_name>\S.*)$")
        match = pattern.match(message.content)
        if match is not None:
            event_name = match.group("event_name")
            new_event: Event = eventcreator.get_event(event_name, message.author.id)
            print("event name", new_event.event_name)
            event_channel = disc_values.event_channel
            await bot.rest.create_message(event_channel, new_event)
            await message.author.send("Your event has been posted!")
            eventcreator.submit_event(message.author.id, event_name)
        else:
            await message.author.send("sorry I couldn't extract the name of the event")


@bot.command
@lightbulb.add_checks(lightbulb.has_roles(disc_values.enigma_role_id))
@lightbulb.option("event_name", "Name of the event", str)
@lightbulb.option("event_link", "Link to facebook event", str)
@lightbulb.command('addevent', 'start an event submission')
@lightbulb.implements(lightbulb.SlashCommand)
async def add_event(ctx: lightbulb.SlashContext):
    print("add event")
    event_channel = disc_values.event_channel
    await bot.rest.create_message(event_channel, f"**{ctx.options.event_name}**\n{ctx.options.event_link}")
    await ctx.respond(ctx.options.event_name)
    try:
        eventcreator.initialize_event(ctx.options.event_name, ctx.author.id, ctx.options.event_link)
    except eventcreator.DuplicateEventError as e:
        await ctx.author.send(
            f'You already have an event with this name, please delete it first with the command: \n\n'
            f'`@Enigma-event-bot#1500 delete-event: {ctx.options.event_name}`')
    else:
        await ctx.author.send(
            "Thank you for using \"Enigma Event Bot\"! Your event will be added shortly, please provide"
            f' a description in the next message, prefixed with:'
            f' \n\n`@Enigma-event-bot#1500 name:{ctx.options.event_name} description:`')


if __name__ == '__main__':
    bot.run()
