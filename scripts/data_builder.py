from faker import Faker
import pandas as pd
import random
import os

fake = Faker(locale='ru_RU')
df = pd.read_csv(os.path.join('data', 'airports_rus.csv'))

TAGS = ['PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'AIRPORT', 'CITY', 'COUNTRY', 'FLIGHT', 'TIME', 'DATE']

def getRandomData(tag):
    global df
    DATAGEN = {
        'PHONE': fake.phone_number(),
        'PASSPORT': fake.passport_number(),
        'NAME': fake.name(),
        'DOB': fake.date_of_birth(),
        'EMAIL': fake.email(),
        'AIRPORT': '', #random.choice(df[random.choice(['Название аэропорта', 'Код ИАТА'])].dropna()),
        'FLIGHT': 'NONE',
        'CITY': fake.city_name(),
        'TIME': fake.time(),
        'DATE': fake.date()
    }
    return DATAGEN[tag]


def replaceAndLabel(message):
    
    global TAGS

    obj = {
        'text': message,
        'entities': []
    }

    tmp_entities = {}

    # inserting generated data
    for tag in TAGS:

        if tag in message:
            split_message = [part for part in obj['text'].split(tag)]
            augmented_message = ''
            
            for i in range(len(split_message) - 1):
                rnd_data = str(getRandomData(tag))
                tmp_entities[rnd_data] = tag
                augmented_message += f'{split_message[i]}{rnd_data}'
                
                if i == len(split_message) - 2:
                    augmented_message += split_message[i + 1]
            
            obj['text'] = augmented_message
    
    # marking out the message
    for key in tmp_entities:
        obj['entities'].append((obj['text'].find(key), obj['text'].find(key) + len(key), tmp_entities[key]))
    
    return obj
    

if __name__ == '__main__':
    import json
    with open('data/raw_data.json', 'r') as f:
        raw_data = json.load(f)
    
    processed_data = []

    for obj in raw_data:
        processed_data.append(replaceAndLabel(obj['message']))

    with open('data/processed_data.json', 'w', encoding='utf-8') as f:
        f.truncate(0)
        json.dump(processed_data, f, ensure_ascii=False, indent=1, separators=(',', ': '))

