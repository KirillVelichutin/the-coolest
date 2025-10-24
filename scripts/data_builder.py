from faker import Faker
import pandas as pd
import random
import os

from generators import setup_faker_providers, get_all_document_types

fake = Faker(locale='ru_RU')
fake = setup_faker_providers(fake)  # добавляем кастомные провайдеры!
df = pd.read_csv(os.path.join('data', 'airports_rus.csv'))

BASE_TAGS = ['PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'AIRPORT', 'CITY', 'COUNTRY', 'FLIGHT', 'TIME', 'DATE',] # 'TICKET']
OTHER_TAGS = get_all_document_types()
TAGS = BASE_TAGS + OTHER_TAGS

DATAGEN = {
    'PHONE': lambda: fake.phone_number(),
    'PASSPORT': lambda: fake.passport_number(),
    'NAME': lambda: fake.name(),
    'DOB': lambda: fake.date_of_birth(),
    'EMAIL': lambda: fake.email(),
    'AIRPORT': lambda: random.choice(df[random.choice(['Название аэропорта', 'Код ИАТА'])].dropna().reset_index(drop=True)),
    # 'TICKET': lambda: ''.join([str(random.randint(0, 9)) for _ in range(13)]), 
    'FLIGHT': lambda: f"{random.choice(['SU', 'AF', 'LH', 'TK', 'BA', 'AY', 'S7', 'U6'])}{random.randint(100, 9999)}",
    'CITY': lambda: fake.city_name(),
    'TIME': lambda: fake.time(),
    'DATE': lambda: fake.date(),
    'INTERNATIONAL_PASSPORT': lambda: fake.international_passport(),
    'BIRTH_CERTIFICATE': lambda: fake.birth_certificate(),
    'VISA': lambda: fake.visa(),
    'TICKET_NUMBER': lambda: fake.ticket_number(),
    'BOOKING_REF': lambda: fake.booking_ref(),
    'BOARDING_PASS': lambda: fake.boarding_pass(),
    'EMD_NUMBER': lambda: fake.emd_number(),
    'ORDER_NUMBER': lambda: fake.order_number()
}



def replaceAndLabel(message):
    
    global TAGS, DATAGEN

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
                rnd_data = str(DATAGEN[tag]())
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
    # import json
    # with open('data/raw_data_ts.json', 'r') as f:
    #     raw_data = json.load(f)
    
    # processed_data = []

    # for obj in raw_data:
    #     processed_data.append(replaceAndLabel(obj['message']))

    # with open('data/processed_data_ts.json', 'w', encoding='utf-8') as f:
    #     f.truncate(0)
    #     json.dump(processed_data, f, ensure_ascii=False, indent=1, separators=(',', ': '))

    print(replaceAndLabel("Для бизнес-зала нужны данные? Вот: NAME EMAIL PASSPORT AIRPORT"))
