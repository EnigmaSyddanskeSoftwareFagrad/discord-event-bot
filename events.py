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
    name: str
    link: str
    organizer_id: int
    state: EventState = field(default=EventState.in_progress)
    description: str | None = field(default=None)
    uuid: int = field(default=uuid.uuid4().int)
    image_link: str | None = field(default=None)

    def __eq__(self, other: 'Event') -> bool:
        return self.name == other.name

    @staticmethod
    def from_dict(data: dict) -> 'Event':
        uuid = data['uuid']
        event_name = data['name']
        event_link = data['link']
        organizer_id = data['organizer_id']
        state = EventState(data['state'])
        image_link = data.get('image_link', None)
        description = data.get('description', None)
        return Event(event_name, event_link, organizer_id, state, description, image_link=image_link)

    def to_dict(self) -> dict:
        return {
            'uuid': self.uuid,
            'name': self.name,
            'link': self.link,
            'organizer_id': self.organizer_id,
            'state': self.state.value,
            'image_link': self.image_link,
            'description': self.description
        }

    def __str__(self):
        return f"***{self.name}***\n{self.description}\n\nLink: {self.link} \n\n {self.image_link}"

    def __hash__(self) -> int:
        return id(self)


class EventManager(MutableSet):
    def __enter__(self) -> 'EventManager':
        self.events = load_events()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_events(self.events)

    def __contains__(self, event: Event) -> bool:
        return event in self.events

    def __iter__(self):
        return iter(self.events)

    def __len__(self) -> int:
        return len(self.events)

    def __getitem__(self, event_name: str) -> Event:
        matches_event = lambda event: event.name == event_name
        event = find(self.events, matches_event)
        if event is not None:
            return event
        else:
            raise EventNotFoundError()

    def add(self, event: Event):
        try:
            self[event.name]
        except EventNotFoundError:
            self.events.add(event)
        else:
            raise DuplicateEventError()

    def edit_event(self, event_name: str, user_id: int, event_link: str):
        try:
            self.remove(event_name)
        except EventNotFoundError:
            pass

        self.add(Event(event_name, event_link, user_id))

    def discard(self, event_name: str):
        event = self[event_name]
        return self.events.discard(event)

    def remove(self, event_name: str) -> None:
        event = self[event_name]
        self.events.remove(event)

    def set_event_description(self, event_name: str, event_description: str):
        event = self[event_name]
        event.description = event_description

    def set_image_link(self, event_name: str, image_link: str):
        event = self[event_name]
        event.image_link = image_link

    def submit_event(self, event_name: str):
        print("submitting event")
        event = self[event_name]
        event.state = EventState.submitted

    def get_in_progress_events(self) -> set[Event]:
        return set(event for event in self.events if event.state == EventState.in_progress)

    def get_submitted_events(self) -> set[Event]:
        return set(event for event in self.events if event.state == EventState.submitted)

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
        json.dump([event.to_dict() for event in events], events_file, indent=4)


if __name__ == '__main__':
    pattern = re.compile(r"^<@\d+> post name:(?P<event_name>.*?)$")
    match = pattern.match("<@1101475630807253002> post name:IT DAY!!! 2023")
    if match is not None:
        print(match.group("event_name"))
    import requests

    url = 'https://avatars.githubusercontent.com/u/112754344?s=200&v=4'
    response = requests.get(url)

    if response.status_code == 200:
        content_type = response.headers['content-type']
        if 'image' in content_type:
            print('This is a valid image URL.')
        else:
            print('This is not an image URL.')
    else:
        print('Failed to retrieve the URL.')
