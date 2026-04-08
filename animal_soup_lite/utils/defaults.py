import json
import os

CONFIG = {"LIFT": [157, 177, 199, 212], "GRAB": [223, 245, 123, 130]}


def save():
    json.dump(CONFIG, open("defaults.json", "w"), indent=4)


def load():
    if os.path.exists("defaults.json"):
        CONFIG.update(json.load(open("defaults.json")))
