import json


class confmanager:
    def __init__(self):
        config_file = open('config.json')
        self.config = json.load(config_file)
        self.token = self.config["TOKEN"]
        self.event_channel = self.config["EVENT_CHANNEL_ID"]
        self.enigma_role_id = self.config["ENIGMA_ROLE_ID"]
        config_file.close()
    def get_token(self):
        return self.token

    def get_event_channel(self):
        return self.event_channel
    def get_enigma_role_id(self):
        return self.enigma_role_id
