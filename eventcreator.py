from dataclasses import dataclass, field
import json
import re
from typing import Callable, Iterable, Optional, Self, TypeVar
import uuid
from enum import Enum
import os

class EventState(Enum):
    in_progress = 'in_progress'
    submitted = 'submitted'

class DuplicateEventError(Exception):
    pass
class EventNotFoundError(Exception):
    pass

@dataclass
class Event:
    uuid: int
    event_name: str
    event_link: str
    organizer_id: int
    state: EventState
    description: str | None = field(default=None)

    @staticmethod
    def from_dict(data: dict) -> 'Event':
        uuid = data['uuid']
        event_name = data['event_name']
        event_link = data['event_link']
        organizer_id = data['organizer_id']
        state = EventState(data['state'])
        description = data.get('description', None)
        return Event(uuid, event_name, event_link, organizer_id, state, description)

    def __str__(self):
        return f"***{self.event_name}***\n{self.description}\n\nLink: {self.event_link}"

EVENTS_FILE_PATH = 'statefiles'
EVENTS_FILE_NAME = f'{EVENTS_FILE_PATH}/events.json'

def load_events() -> list[Event]:
    if not os.path.exists(EVENTS_FILE_NAME):
        return []

    with open(EVENTS_FILE_NAME) as events_file:
        events_dict: list[dict] = json.load(events_file)

    events: list[Event] = [Event.from_dict(event) for event in events_dict]
    return events

def save_events(events: list[Event]):
    # create parent folders if they don't exist
    os.makedirs(EVENTS_FILE_PATH, exist_ok=True)
    with open(EVENTS_FILE_NAME, 'w+') as events_file:
        json.dump(events, events_file)


def initialize_event(event_name: str, user_id: int, event_link: str):
    events = load_events()
    # if the event already exists, raise error
    if find_event(events, event_name=event_name, user_id=user_id) is not None:
        raise DuplicateEventError()

    event = Event(
        uuid=uuid.uuid4().int,
        event_name=event_name,
        event_link=event_link,
        organizer_id=user_id,
        state=EventState.in_progress
    )
    events.append(event)

    save_events(events)

def override_event(event_name: str, user_id: int, event_link: str):
    events = load_events()
    event = find_event(events, event_name, user_id)
    if event is not None:
        events.remove(event)
        save_events(events)

    initialize_event(event_name, user_id, event_link)

def delete_event(event_name: str, user_id: int | None = None):
    events = load_events()

    event = find_event(events, event_name=event_name, user_id=user_id)
    if event is None:
        raise EventNotFoundError

    events.remove(event)
    save_events(events)

def set_event_description(event_name: str, user_id: int, event_description: str):
    events = load_events()
    event = find_event(events, event_name, user_id)
    if event is None:
        raise EventNotFoundError

    event.description = event_description
    save_events(events)

def events_by_user(user_id: int) -> list:
    events = load_events()
    return [event for event in events if event.organizer_id == user_id]

def submit_event(user_id: int, event_name: str):
    events = load_events()
    event = find_event(events, event_name, user_id)
    if event is None:
        raise EventNotFoundError

    event.state = EventState.submitted
    save_events(events)

def get_event(event_name: str, user_id: int) -> Event:
    events = load_events()
    event = find_event(events, event_name, user_id)
    if event is not None:
        print("event found: ", event)
        return event
    else:
        print(f'Event not found: {event_name} {user_id}')
        raise EventNotFoundError

def find_event(events: list[Event], event_name: str, user_id: int | None = None) -> Event | None:
    if user_id is not None:
        matches_event = lambda event: event["user_id"] == user_id and event["event_name"] == event_name
    else:
        matches_event = lambda event: event["event_name"] == event_name
    return find(events, matches_event)

T = TypeVar('T')
def find(collection: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    for element in collection:
        if predicate(element):
            return element


if __name__ == '__main__':
    pattern = re.compile(r"^<@\d+> post name:(?P<event_name>.*?)$")
    match = pattern.match("<@1101475630807253002> post name:IT DAY!!! 2023")
    if match is not None:
        event_name = match.group("event_name")
        print(event_name)
