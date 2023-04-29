from dataclasses import dataclass
import json

@dataclass
class ConfManager:
    token: str
    event_channel: int
    enigma_role_id: int

    def __init__(self):
        with open('config/config.json') as config_file:
            self.config = json.load(config_file)
        self.token = self.config["token"]
        self.event_channel = self.config["event_channel_id"]
        self.enigma_role_id = self.config["enigma_role_id"]
