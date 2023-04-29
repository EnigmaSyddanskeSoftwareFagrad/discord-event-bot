import os
from collections.abc import MutableSet
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import uuid

from utils import find

class EventState(Enum):
    in_progress = 'in_progress'
    submitted = 'submitted'

class DuplicateEventError(Exception):
    pass
class EventNotFoundError(Exception):
    pass

@dataclass
class Event:
    event_name: str
    event_link: str
    organizer_id: int
    state: EventState = field(default=EventState.in_progress)
    description: str | None = field(default=None)
    uuid: int = field(default=uuid.uuid4().int)

    @staticmethod
    def from_dict(data: dict) -> 'Event':
        uuid = data['uuid']
        event_name = data['event_name']
        event_link = data['event_link']
        organizer_id = data['organizer_id']
        state = EventState(data['state'])
        description = data.get('description', None)
        return Event(event_name, event_link, organizer_id, state, description)

    def __str__(self):
        return f"***{self.event_name}***\n{self.description}\n\nLink: {self.event_link}"

class EventManager(MutableSet):
    def __enter__(self) -> 'EventManager':
        self.events = load_events()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_events(self.events)

    def __contains__(self, event: Event) -> bool:
        return event in self.events

    def get_event(self, event_name: str, user_id: int | None = None) -> Event | None:
        if user_id is not None:
            matches_event = lambda event: event["user_id"] == user_id and event["event_name"] == event_name
        else:
            matches_event = lambda event: event["event_name"] == event_name
        return find(self.events, matches_event)

    def add_event(self, event: Event):
        # if the event already exists, raise error
        if self.get_event(event.event_name, event.organizer_id) is not None:
            raise DuplicateEventError()

        self.events.add(event)

    def override_event(self, event_name: str, user_id: int, event_link: str):
        event = self.get_event(event_name, user_id)
        if event is not None:
            self.events.remove(event)

        self.add_event(Event(event_name, event_link, user_id))

    def get_event_or_error(self, event_name: str, user_id: int | None = None) -> Event:
        event = self.get_event(event_name, user_id)
        if event is None:
            raise EventNotFoundError
        else:
            return event

    def remove_event(self, event_name: str, user_id: int | None = None):
        event = self.get_event_or_error(event_name, user_id)
        self.events.remove(event)

    def set_event_description(self, event_name: str, user_id: int, event_description: str):
        event = self.get_event_or_error(event_name, user_id)
        event.description = event_description

    def submit_event(self, user_id: int, event_name: str):
        event = self.get_event_or_error(event_name, user_id)
        event.state = EventState.submitted


EVENTS_FILE_PATH = 'statefiles'
EVENTS_FILE_NAME = f'{EVENTS_FILE_PATH}/events.json'

def load_events() -> set[Event]:
    if not os.path.exists(EVENTS_FILE_NAME):
        return set()

    with open(EVENTS_FILE_NAME) as events_file:
        events_dict: set[dict] = json.load(events_file)

    events: set[Event] = set(Event.from_dict(event) for event in events_dict)
    return events

def save_events(events: set[Event]):
    # create parent folders if they don't exist
    os.makedirs(EVENTS_FILE_PATH, exist_ok=True)
    with open(EVENTS_FILE_NAME, 'w+') as events_file:
        json.dump(events, events_file)


if __name__ == '__main__':
    pattern = re.compile(r"^<@\d+> post name:(?P<event_name>.*?)$")
    match = pattern.match("<@1101475630807253002> post name:IT DAY!!! 2023")
    if match is not None:
        print(match.group("event_name"))
