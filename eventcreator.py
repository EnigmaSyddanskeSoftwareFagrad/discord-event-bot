import json
import re
import string
from typing import Callable, Iterable, TypeVar
import uuid
from enum import Enum

class Event:
    def __init__(self, event_name: string, event_link: string, description: string):
        self.event_name = event_name
        self.event_link = event_link
        self.description = description

    def __str__(self):
        return f"***{self.event_name}***\n{self.description}\n\nLink: {self.event_link}"

class ResponseCode(Enum):
    OK = 200
    DUPLICATE = 409
    NOT_FOUND = 404

IN_PROGRESS_FILE_NAME = 'statefiles/event-in-progress.json'
SUBMITTED_FILE_NAME = 'statefiles/event-submitted.json'

def initialize_event(event_name: string, user_id: int, event_link: string) -> ResponseCode:
    with open(IN_PROGRESS_FILE_NAME) as f:
        in_progress_data: list = json.load(f)

    if find_event(in_progress_data, event_name=event_name, user_id=user_id) is not None:
        return ResponseCode.DUPLICATE

    event = {
        "UUID": uuid.uuid4().int,
        "user_id": user_id,
        "event_name": event_name,
        "event_link": event_link,
    }
    in_progress_data.append(event)

    with open(IN_PROGRESS_FILE_NAME, 'w') as w:
        json.dump(in_progress_data, w, indent=4)

    return ResponseCode.OK

def override_event(event_name: string, user_id: int, event_link: string):
    with open(IN_PROGRESS_FILE_NAME) as f:
        in_progress_data: list = json.load(f)

    event = find_event(in_progress_data, event_name, user_id)
    if event is not None:
        in_progress_data.remove(event)
        with open(IN_PROGRESS_FILE_NAME, 'w') as w:
            json.dump(in_progress_data, w, indent=4)

    initialize_event(user_id, event_name, event_link)
    return ResponseCode.OK

def delete_in_progress_event(event_name: string, user_id: int = None):
    with open(IN_PROGRESS_FILE_NAME) as f:
        in_progress_data: list = json.load(f)

    event = find_event(event_name=event_name, user_id=user_id)
    if event is not None:
        in_progress_data.remove(event)
        with open(IN_PROGRESS_FILE_NAME, 'w') as w:
            json.dump(in_progress_data, w, indent=4)
        return ResponseCode.OK
    else:
        return ResponseCode.NOT_FOUND

def set_event_description(event_name: string, user_id: int, event_description: string) -> ResponseCode:
    with open(IN_PROGRESS_FILE_NAME) as f:
        in_progress_data = json.load(f)

    event = find_event(in_progress_data, event_name, user_id)
    if event is not None:
        event["event_description"] = event_description
        with open(IN_PROGRESS_FILE_NAME, 'w') as w:
            json.dump(in_progress_data, w, indent=4)
        return ResponseCode.OK
    else:
        return ResponseCode.NOT_FOUND

def in_progress_events_by_user(user_id: int) -> list:
    with open(IN_PROGRESS_FILE_NAME) as f:
        in_progress_data = json.load(f)
    return [event for event in in_progress_data if event["user_id"] == user_id]

T = TypeVar('T')
def find(collection: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    for element in collection:
        if predicate(element):
            return element

def submit_event(user_id: int, event_name: string) -> ResponseCode:
    with open(IN_PROGRESS_FILE_NAME, 'r') as in_progress_file:
        in_progress_data: list[dict] = json.load(in_progress_file)
    with open(SUBMITTED_FILE_NAME, 'r') as submitted_file:
        submitted_data: list[dict] = json.load(submitted_file)

    # pop the correct event from in_progress
    event_to_move = find_event(in_progress_data, event_name, user_id)
    in_progress_data.remove(event_to_move)

    # insert the event into submitted
    submitted_data.append(event_to_move)

    with open(IN_PROGRESS_FILE_NAME, 'w') as in_progress_file:
        json.dump(in_progress_data, in_progress_file, indent=4)
    with open(SUBMITTED_FILE_NAME, 'w') as submitted_file:
        json.dump(submitted_data, submitted_file, indent=4)
    return ResponseCode.OK

def get_in_progress_event(event_name: string, user_id: int) -> Event | None:
    with open(IN_PROGRESS_FILE_NAME) as f:
        submitted_data = json.load(f)

    event = find_event(submitted_data, event_name, user_id)
    if event is not None:
        print("event found: ", event)
        return Event(event["event_name"], event["event_link"], event["event_description"])
    else:
        print(f'Event not found: {event_name} {user_id}')
        return None

def find_event(events: list, event_name: str, user_id: int | None = None) -> dict | None:
    if user_id is not None:
        matches_event = lambda event: event["user_id"] == user_id and event["event_name"] == event_name
    else:
        matches_event = lambda event: event["event_name"] == event_name
    return find(events, matches_event)


if __name__ == '__main__':
    pattern = re.compile(r"^<@\d+> post name:(?P<event_name>.*?)$")
    event_name = pattern.match("<@1101475630807253002> post name:IT DAY!!! 2023").group("event_name")
    print(event_name)
