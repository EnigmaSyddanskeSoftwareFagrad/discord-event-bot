import re
import hikari
import miru
from hikari.events import message_events
import lightbulb
from configmanager import ConfigManager
from events import Event, EventManager, DuplicateEventError
import eventviews
import datetime
from roleview import RoleView

config = ConfigManager()
bot = lightbulb.BotApp(token=config.token)
miru.install(bot)
year_roles: dict[int, hikari.Role.id] = {}

new_event_qualifier = "new event qualifier"
post_event_qualifier = "post event qualifier"


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human: return
    if not event.message.user_mentions_ids: return

    if bot.get_me().id in event.message.user_mentions_ids:
        await event.message.respond("Pong!")


@bot.listen()
async def on_event_description(message: hikari.GuildMessageCreateEvent) -> None:
    (is_reply, event) = is_reply_action(new_event_qualifier, message)
    if not is_reply:
        return
    prototype_channel = config.event_prototype_channel
    print("on event description")
    print(message.content)
    pattern = r'https?:\/\/[^ ]+\.(png|jpg|svg|webp)'
    img_link = message.content.split("\n")[0]
    event_description = message.content.removeprefix(img_link + "\n")
    print(f'{event_description = }')
    match = event.split("\n")
    event_name = match[0].replace("**", "")
    print(f'{event_name = }')
    with EventManager() as eventmanager:
        eventmanager.set_event_description(event_name, event_description)
        eventmanager.set_image_link(event_name, img_link)
        new_event: Event = eventmanager[event_name]
        print("event name", new_event.name)

        await bot.rest.create_message(prototype_channel,
                                      "your event will be represented like this without the qualifier:\n")
        await bot.rest.create_message(prototype_channel, f"{post_event_qualifier}\n{new_event}")
        await bot.rest.create_message(prototype_channel,
                                      f"If you want to change your event, "
                                      f"you can redo this step by"
                                      f"replying to the message that starts with: {new_event_qualifier} \n "
                                      )


@bot.listen()
async def on_event_post(message: hikari.GuildMessageCreateEvent) -> None:
    (is_reply, event) = is_reply_action(post_event_qualifier, message)
    if not is_reply:
        return
    print("on event post")
    event_name = event.split("\n")[0].replace("***", "")
    print(f'{event_name = }')
    with EventManager() as eventmanager:
        new_event: Event = eventmanager[event_name]
        embed = hikari.Embed(title=event_name, description=str(new_event.description), url=new_event.link,
                             color=0x00ff00)
        embed.set_image(new_event.image_link)
        embed.set_author(name="Enigma", icon="https://avatars.githubusercontent.com/u/112754344?s=200&v=4")
        embed.set_footer(text="Syddanske Softwarestuderendes Fagråd")
        print("event name", new_event.name)
        event_channel = config.event_channel
        view = eventviews.EventView(timeout=60)
        event_post = await bot.rest.create_message(event_channel, components=view, embed=embed,
                                                flags=hikari.MessageFlag.EPHEMERAL)
        await view.start(event_post)
        await message.message.add_reaction("👍")
        eventmanager.submit_event(event_name)


@bot.command
@lightbulb.add_checks(lightbulb.has_roles(config.enigma_role_id))
@lightbulb.option("event_name", "Name of the event", str)
@lightbulb.option("event_link", "Link to facebook event", str)
@lightbulb.command('addevent', 'start an event submission')
@lightbulb.implements(lightbulb.SlashCommand)
async def add(ctx: lightbulb.SlashContext):
    ''' Message structure is as follows:
        Line 1: qualifier
        Line 2: event name
    '''
    print("add event")
    prototype_channel = config.event_prototype_channel
    if "\n" in ctx.options.event_name:
        await ctx.respond("event name cannot contain newline \n aborting....")
    await bot.rest.create_message(prototype_channel,
                                  f"{new_event_qualifier}\n"
                                  f"**{ctx.options.event_name}**\n{ctx.options.event_link} \n under construction, "
                                  "Thank you for using \"Enigma Event Bot\"! Your event will be added shortly, "
                                  "please reply with a description and a picture.")
    try:
        with EventManager() as eventmanager:
            eventmanager.add(Event(ctx.options.event_name, ctx.options.event_link, ctx.author.id))
    except DuplicateEventError as e:
        await ctx.respond(
            f'You already have an event with this name, please delete it first with the command: \n\n'
            f'`<@{bot.get_me().id}> delete-event: {ctx.options.event_name}`')


@bot.command
@lightbulb.add_checks(lightbulb.has_roles(config.enigma_role_id))
@lightbulb.command("update_years", 'Add 5 subsequent years as roles')
@lightbulb.implements(lightbulb.SlashCommand)
async def update_year(ctx: lightbulb.SlashContext):
    # THIS LOOP IS ONLY FOR TESTING
    # for role in await bot.rest.fetch_roles(config.guild_id):
    #    if role.name.startswith("20"):
    #        await bot.rest.delete_role(role=role, guild=config.guild_id)

    years = [datetime.date.today().year - i for i in range(6)]
    for year, role in year_roles.items():
        if year not in years:
            await bot.rest.delete_role(role, config.guild_id)
            await ctx.respond(f"deleted role: {year}")
            del year_roles[year]

    for year in years:
        if year not in year_roles.keys():
            created_role = await bot.rest.create_role(name=str(year), guild=config.guild_id, color=0x00ff00, hoist=True,
                                                      mentionable=True)
            await ctx.respond(f"added role: {year}")
            year_roles[year] = created_role
    await ctx.respond("done")
    role_view = RoleView(year_roles)
    message = await bot.rest.create_message(config.role_channel, components=role_view,
                                            content="React to this message to get your year role!")
    await role_view.start(message)


def is_reply_action(reply_qualifier: str, event: hikari.GuildMessageCreateEvent) -> (bool, str):
    """ returns a tuple of (is_reply, reply_content) reply_content is without the reply qualifier"""
    if not event.is_human or event.message.content is None:
        return False, None
    if event.channel_id is config.event_prototype_channel or event.message.type is not event.message.type.REPLY:
        print("not a reply")
        return False, None
    if event.message.referenced_message.author.id != bot.get_me().id:
        print("not a reply to me")
        print(event.message.referenced_message.author.id)
        print(bot.get_me().id)
        return False, None
    if event.message.referenced_message.content is None:
        print("no content")
        return False, None
    if not event.message.referenced_message.content.startswith(reply_qualifier):
        return False, None
    return True, event.message.referenced_message.content.removeprefix(reply_qualifier + "\n").strip()


if __name__ == '__main__':
    bot.run()
