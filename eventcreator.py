import json
import re
import string
import uuid
from enum import Enum


class Event:
    def __init__(self, event_name: string, event_link: string, description: string):
        self.event_name = event_name
        self.event_link = event_link
        self.description = description

    def __str__(self):
        return f"***{self.event_name}***\n{self.description}\n\nLink: {self.event_link}"

class ResponseCodes(Enum):
    OK = 200
    DUPLICATE = 409
    NOT_FOUND = 404


INPROGRESS_FILE_NAME = 'statefiles/event-inprogress.json'
SUBMITTED_FILE_NAME = 'statefiles/event-submitted.json'


def initialize_event(event_name: string, user_id: int, event_link: string):
    with open(INPROGRESS_FILE_NAME) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data:
        if event["user_id"] == user_id and event["event_name"] == event_name:
            return ResponseCodes.DUPLICATE
    event = {
        "UUID": uuid.uuid4().int,
        "user_id": user_id,
        "event_name": event_name,
        "event_link": event_link,
    }
    inprogress_data.append(event)
    with open(INPROGRESS_FILE_NAME, 'w') as w:
        json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    return ResponseCodes.OK


def override_event(event_name: string, user_id: int, event_link: string):
    is_event_found = False
    with open(INPROGRESS_FILE_NAME) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data.copy():
        if event["user_id"] == user_id and event["event_name"] == event_name:
            inprogress_data.remove(event)
            is_event_found = True
    with open(INPROGRESS_FILE_NAME, 'w') as w:
        json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    initialize_event(user_id, event_name, event_link)
    if is_event_found:
        return ResponseCodes.OK
    return ResponseCodes.NOT_FOUND


def delete_inprogress_event(event_name: string, user_id: int = None):
    with open(INPROGRESS_FILE_NAME) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data.copy():
        if event["user_id"] == user_id or user_id is None and event["event_name"] == event_name:
            inprogress_data.remove(event)
            with open(INPROGRESS_FILE_NAME, 'w') as w:
                json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
            return ResponseCodes.OK
    return ResponseCodes.NOT_FOUND


def set_event_description(event_name: string, user_id: int, event_description: string):
    is_overwrite = False
    with open(INPROGRESS_FILE_NAME) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data:
        if event["user_id"] == user_id and event["event_name"] == event_name:
            event["event_description"] = event_description
            is_overwrite = True
    with open(INPROGRESS_FILE_NAME, 'w') as w:
        json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    if is_overwrite:
        return ResponseCodes.OK
    return ResponseCodes.NOT_FOUND


def check_inprogress_events_from_user(user_id: int):
    with open(INPROGRESS_FILE_NAME) as f:
        inprogress_data = json.load(f)
    events: list = []
    for event in inprogress_data:
        if event["user_id"] == user_id:
            events.append(event)
    return events


def submit_event(user_id: int, event_name: string):
    submitted_event = None
    with open(INPROGRESS_FILE_NAME) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data.copy():
        if event["user_id"] == user_id and event["event_name"] == event_name:
            submitted_event = event
            inprogress_data.remove(event)
            with open(INPROGRESS_FILE_NAME, 'w') as w:
                json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    with open('statefiles/event-submitted.json') as f:
        submitted_data = json.load(f)
    submitted_data.append(submitted_event)
    with open('statefiles/event-submitted.json', 'w') as w:
        json.dump(submitted_data, w, indent=4, separators=(',', ':'))
    return ResponseCodes.OK


def get_event(event_name: string, user_id: int):
    with open(INPROGRESS_FILE_NAME) as f:
        submitted_data = json.load(f)
    for event in submitted_data:
        if event["user_id"] == user_id and event["event_name"] == event_name:
            print("event found: ", event)
            return Event(event["event_name"], event["event_link"], event["event_description"])
    print(f'Event not found: {event_name} {user_id}')
    return None


if __name__ == '__main__':
    pattern = re.compile(r"^<@\d+> post name:(?P<event_name>.*?)$")
    event_name = pattern.match("<@1101475630807253002> post name:IT DAY!!! 2023").group("event_name")
    print(event_name)
