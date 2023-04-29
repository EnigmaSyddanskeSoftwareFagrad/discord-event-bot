import re
import hikari
from hikari.events import message_events
import lightbulb
from configmanager import ConfigManager
from events import Event, EventManager, DuplicateEventError

config = ConfigManager()
bot = lightbulb.BotApp(token=config.token)

@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human: return
    if not event.message.user_mentions_ids: return

    if bot.get_me().id in event.message.user_mentions_ids:
        await event.message.respond("Pong!")

@bot.listen()
async def on_event_description(event: message_events.DMMessageCreateEvent) -> None:
    if not event.is_human: return
    message = event.message
    print("on event description")
    print(message.content)
    if message.content is None: return
    if message.content.startswith(f'<@{bot.get_me().id}> name:'):
        pattern = re.compile(r"^<@\d+> name:\s*(?P<event_name>\S.*) description:")
        match = pattern.match(message.content)
        if match:
            event_name = match.group("event_name")
            print(f'{event_name = }')
            description = message.content.removeprefix(f"<@{bot.get_me().id}> name:{event_name} description:").strip()
            with EventManager() as eventmanager:
                eventmanager.set_event_description(event_name, description)
                await message.author.send("Thank you for using \"Enigma Event Bot\"! "
                                            "Your event will be added shortly...")
                new_event: Event = eventmanager[event_name]
            print("event name", new_event.name)

            await message.author.send("your event will be represented like this:\n")
            await message.author.send(new_event)
            await message.author.send("If you want to change the description of your event"
                                            " repeat your last message with the new description.\n\n"
                                            "if you want to post your event send:\n"
                                            f"`<@{bot.get_me().id}> post name:{event_name}`")
        else:
            await message.author.send("sorry I couldn't extract the name of the event")

@bot.listen()
async def on_event_post(event: message_events.DMMessageCreateEvent) -> None:
    if not event.is_human: return
    message = event.message
    print("on event post")
    print(message.content)
    if message.content is None: return
    if message.content.startswith(f'<@{bot.get_me().id}> post name:'):
        pattern = re.compile(r"^<@\d+> post name:\s*(?P<event_name>\S.*)$")
        match = pattern.match(message.content)
        if match is not None:
            event_name = match.group("event_name")
            with EventManager() as eventmanager:
                new_event: Event = eventmanager[event_name]
                print("event name", new_event.name)
                event_channel = config.event_channel
                await bot.rest.create_message(event_channel, new_event)
                await message.author.send("Your event has been posted!")
                eventmanager.submit_event(event_name)
        else:
            await message.author.send("sorry I couldn't extract the name of the event")


@bot.command
@lightbulb.add_checks(lightbulb.has_roles(config.enigma_role_id))
@lightbulb.option("event_name", "Name of the event", str)
@lightbulb.option("event_link", "Link to facebook event", str)
@lightbulb.command('addevent', 'start an event submission')
@lightbulb.implements(lightbulb.SlashCommand)
async def add(ctx: lightbulb.SlashContext):
    print("add event")
    event_channel = config.event_channel
    await bot.rest.create_message(event_channel, f"**{ctx.options.event_name}**\n{ctx.options.event_link}")
    await ctx.respond(ctx.options.event_name)
    try:
        with EventManager() as eventmanager:
            eventmanager.add(Event(ctx.options.event_name, ctx.options.event_link, ctx.author.id))
    except DuplicateEventError as e:
        await ctx.author.send(
            f'You already have an event with this name, please delete it first with the command: \n\n'
            f'`<@{bot.get_me().id}> delete-event: {ctx.options.event_name}`')
    else:
        await ctx.author.send(
            "Thank you for using \"Enigma Event Bot\"! Your event will be added shortly, please provide"
            f' a description in the next message, prefixed with:'
            f' \n\n`<@{bot.get_me().id}> name:{ctx.options.event_name} description:`')


if __name__ == '__main__':
    bot.run()
