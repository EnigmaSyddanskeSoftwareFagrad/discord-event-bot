import json


class ConfManager:
    def __init__(self):
        with open('config/config.json') as config_file:
            self.config = json.load(config_file)
        self.token = self.config["TOKEN"]
        self.event_channel = self.config["EVENT_CHANNEL_ID"]
        self.enigma_role_id = self.config["ENIGMA_ROLE_ID"]
        self.bot_id = self.config["BOT_ID"]
