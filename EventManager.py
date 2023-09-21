#import arrow
import configparser

class TimeManager:
    def __init__(self, name = None, start= None, end = None, img = None, sample = None):
        config = configparser.ConfigParser()
        pass

import json

def get_simple_events():
    with open('main.json', 'r', encoding='utf-8') as config_file:
        config_data = json.load(config_file)

    if 'TimeManager' in config_data:
        event_templates = config_data['TimeManager']['event_templates']
        return event_templates
