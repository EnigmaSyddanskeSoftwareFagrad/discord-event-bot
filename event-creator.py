import json
import uuid
from enum import Enum


class ResponseCodes(Enum):
    OK = 200
    DUPLICATE = 409
    NOT_FOUND = 404


def initialize_event(event_name, user_id, event_link):
    inprogress_file_name = '../event-inprogress.json'
    with open(inprogress_file_name) as f:
        inprogress_data = json.load(f)
    print(inprogress_data)
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
    with open(inprogress_file_name, 'w') as w:
        json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    return ResponseCodes.OK


def override_event(event_name, user_id, event_link):
    inprogress_file_name = '../event-inprogress.json'
    is_event_found = False
    with open(inprogress_file_name) as f:
        inprogress_data = json.load(f)
    print(inprogress_data)
    for event in inprogress_data.copy():
        print("event!")
        if event["user_id"] == user_id and event["event_name"] == event_name:
            inprogress_data.remove(event)
            is_event_found = True
            print("deleted event")
    with open(inprogress_file_name, 'w') as w:
        json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    initialize_event(user_id, event_name, event_link)
    if is_event_found:
        return ResponseCodes.OK
    return ResponseCodes.NOT_FOUND


def delete_inprogress_event(event_name, user_id=None):
    inprogress_file_name = '../event-inprogress.json'
    with open(inprogress_file_name) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data.copy():
        print(event)
        if event["user_id"] == user_id or user_id is None and event["event_name"] == event_name:
            inprogress_data.remove(event)
            with open(inprogress_file_name, 'w') as w:
                json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
            return ResponseCodes.OK
    return ResponseCodes.NOT_FOUND


def set_event_description(event_name, user_id, event_description):
    inprogress_file_name = '../event-inprogress.json'
    is_overwrite = False
    with open(inprogress_file_name) as f:
        inprogress_data = json.load(f)
    for event in inprogress_data:
        print(event)
        if event["user_id"] == user_id and event["event_name"] == event_name:
            event["event_description"] = event_description
            is_overwrite = True
    with open(inprogress_file_name, 'w') as w:
        json.dump(inprogress_data, w, indent=4, separators=(',', ':'))
    if is_overwrite:
        return ResponseCodes.OK
    return ResponseCodes.NOT_FOUND


def check_inprogress_events_from_user(user_id):
    inprogress_file_name = '../event-inprogress.json'
    with open(inprogress_file_name) as f:
        inprogress_data = json.load(f)
    events: list = []
    for event in inprogress_data:
        if event["user_id"] == user_id:
            events.append(event)
    return events


if __name__ == '__main__':
    print(check_inprogress_events_from_user(123))

