print('code_data')

from faker import Faker
import pandas as pd
import random
import os
import json
from datetime import datetime, timedelta

fake = Faker(locale='ru_RU')

def load_airports_data():
    """Загружает данные об аэропортах из всех доступных файлов"""
    airports_data = []
    
    # Загрузка российских аэропортов
    try:
        ru_airports = pd.read_csv('airports_ru.csv')
        print("Загружены российские аэропорты")
        for _, row in ru_airports.iterrows():
            airport = {
                'name': row['Название аэропорта'],
                'iata': row['Код ИАТА'],
                'icao': row['Код ИКАО'],
                'city': row['Населённый пункт'],
                'region': row['Регион'],
                'type': 'domestic'
            }
            airports_data.append(airport)
    except Exception as e:
        print(f"Ошибка загрузки airports_ru.csv: {e}")

    # Загрузка международных аэропортов
    try:
        intl_airports = pd.read_csv('Airports.csv')
        print("Загружены международные аэропорты")
        for _, row in intl_airports.iterrows():
            airport = {
                'name': row['name'],
                'iata': row['iata_code'],
                'icao': row['icao_code'],
                'city': row['municipality'],
                'country_code': row['iso_country'],
                'type': 'international'
            }
            airports_data.append(airport)
    except Exception as e:
        print(f"Ошибка загрузки Airports.csv: {e}")

    return airports_data

def load_country_codes():
    """Загружает коды стран"""
    try:
        country_codes = pd.read_csv('Country_Codes_Tel.csv')
        print("Загружены коды стран")
        return country_codes
    except Exception as e:
        print(f"Ошибка загрузки Country_Codes_Tel.csv: {e}")
        return pd.DataFrame()

# Загружаем данные
AIRPORTS_DATA = load_airports_data()
COUNTRY_CODES = load_country_codes()

# Фильтруем аэропорты с валидными кодами IATA
VALID_AIRPORTS = [a for a in AIRPORTS_DATA if pd.notna(a.get('iata')) and a['iata'] != '']
if not VALID_AIRPORTS:
    print("Не найдено аэропортов с валидными кодами IATA, создаем заглушки")
    VALID_AIRPORTS = [
        {'name': 'Шереметьево', 'iata': 'SVO', 'icao': 'UUEE', 'city': 'Москва'},
        {'name': 'Домодедово', 'iata': 'DME', 'icao': 'UUDD', 'city': 'Москва'},
        {'name': 'Внуково', 'iata': 'VKO', 'icao': 'UUWW', 'city': 'Москва'},
        {'name': 'Пулково', 'iata': 'LED', 'icao': 'ULLI', 'city': 'Санкт-Петербург'}
    ]

TAGS = ['PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'AIRPORT', 'CITY', 'COUNTRY', 'FLIGHT', 'TIME', 'DATE', 
        'FLIGHT_NUMBER', 'TICKET_NUMBER', 'SEAT_NUMBER', 'ORDER_NUMBER', 'DOCUMENT_TYPE', 'TIMEZONE', 
        'FROM_LOCATION', 'TO_LOCATION', 'DEPARTURE_DATE', 'ARRIVAL_DATE', 'TRANSFERS', 'CLASS', 'AIRLINE', 'BAGGAGE',
        'IATA_CODE', 'ICAO_CODE', 'COUNTRY_CODE', 'BAGGAGE_COUNT', 'BAGGAGE_WEIGHT']

DATAGEN = {
    'PHONE': fake.phone_number,
    'PASSPORT': fake.passport_number,
    'NAME': fake.name,
    'DOB': fake.date_of_birth,
    'EMAIL': fake.email,
    'AIRPORT': lambda: random.choice(VALID_AIRPORTS)['name'],
    'IATA_CODE': lambda: random.choice(VALID_AIRPORTS)['iata'],
    'ICAO_CODE': lambda: random.choice(VALID_AIRPORTS)['icao'],
    'CITY': fake.city_name,
    'COUNTRY': fake.country,
    'FLIGHT': lambda: 'NONE',
    'TIME': fake.time,
    'DATE': fake.date,
    'FLIGHT_NUMBER': lambda: f"{random.choice(['SU', 'AF', 'LH', 'TK', 'BA', 'AY', 'S7', 'U6'])}{random.randint(100, 9999)}",
    'TICKET_NUMBER': lambda: ''.join([str(random.randint(0, 9)) for _ in range(13)]),
    'SEAT_NUMBER': lambda: f"{random.randint(1, 60)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
    'ORDER_NUMBER': lambda: f"ORD{random.randint(100000, 999999)}",
    'DOCUMENT_TYPE': lambda: random.choice(['Паспорт РФ', 'Загранпаспорт', 'Свидетельство о рождении', 'Удостоверение личности', 'Вид на жительство в РФ']),
    'TIMEZONE': lambda: random.choice([f"+{i}" for i in range(1, 13)] + [f"-{i}" for i in range(1, 13)]),
    'FROM_LOCATION': lambda: random.choice(VALID_AIRPORTS)['city'],
    'TO_LOCATION': lambda: random.choice(VALID_AIRPORTS)['city'],
    'DEPARTURE_DATE': lambda: (datetime.now() + timedelta(days=random.randint(1, 365))).strftime("%d.%m.%Y"),
    'ARRIVAL_DATE': lambda: (datetime.now() + timedelta(days=random.randint(2, 370))).strftime("%d.%m.%Y"),
    'TRANSFERS': lambda: str(random.randint(0, 3)),
    'CLASS': lambda: random.choice(['Эконом', 'Бизнес', 'Первый']),
    'AIRLINE': lambda: random.choice(['Аэрофлот', 'S7 Airlines', 'Уральские авиалинии', 'Победа', 'Red Wings', 'Nordwind Airlines', 'Azur Air']),
    'BAGGAGE': lambda: random.choice(['1 место багажа', '2 места багажа', 'только ручная кладь', 'багаж не включен']),
    'BAGGAGE_COUNT': lambda: str(random.randint(0, 3)),
    'BAGGAGE_WEIGHT': lambda: f"{random.randint(5, 32)} кг",
    'COUNTRY_CODE': lambda: random.choice(COUNTRY_CODES['DIALINGCODE'].tolist()) if not COUNTRY_CODES.empty else random.choice(['+7', '+1', '+44', '+49'])
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
                # Если значение в DATAGEN - это функция, вызываем её
                try:
                    if callable(DATAGEN[tag]):
                        rnd_data = str(DATAGEN[tag]())
                    else:
                        rnd_data = str(DATAGEN[tag])
                except Exception as e:
                    print(f"Ошибка генерации данных для тега {tag}: {e}")
                    rnd_data = f"[ОШИБКА_{tag}]"
                    
                tmp_entities[rnd_data] = tag
                augmented_message += f'{split_message[i]}{rnd_data}'

                if i == len(split_message) - 2:
                    augmented_message += split_message[i + 1]

            obj['text'] = augmented_message

    # marking out the message
    for key in tmp_entities:
        start_idx = obj['text'].find(key)
        if start_idx != -1:  # Проверяем, что подстрока найдена
            obj['entities'].append((start_idx, start_idx + len(key), tmp_entities[key]))

    return obj


def load_messages_from_json(filename):
    """Загружает сообщения из JSON файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Обрабатываем разные форматы JSON файла
        if isinstance(data, list):
            # Если это список строк
            if all(isinstance(item, str) for item in data):
                return data
            # Если это список объектов с полем 'text' или 'message'
            elif all(isinstance(item, dict) for item in data):
                messages = []
                for item in data:
                    if 'text' in item:
                        messages.append(item['text'])
                    elif 'message' in item:
                        messages.append(item['message'])
                    elif 'sms' in item:
                        messages.append(item['sms'])
                return messages
        elif isinstance(data, dict):
            # Если это объект с полями, содержащими сообщения
            messages = []
            for key, value in data.items():
                if isinstance(value, str):
                    messages.append(value)
                elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                    messages.extend(value)
            return messages
        
        print(f"Неизвестный формат файла {filename}")
        return []
    
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return []


def main():
    
    # Основная логика - обработка сообщений из файла
    messages = load_messages_from_json('raw_data_ts.json')
    
    if not messages:
        print("Нет сообщений для обработки")
        return
    
    print(f"Загружено {len(messages)} сообщений из raw_data_ts.json")
    print(f"Доступно аэропортов: {len(VALID_AIRPORTS)}")
    
    # Обрабатываем все сообщения
    processed_data = []
    for i, message in enumerate(messages, 1):
        result = replaceAndLabel(message)
        processed_data.append(result)
        if i % 100 == 0:
            print(f"Обработано сообщение {i}/{len(messages)}")
    
    # Сохраняем в JSON файл
    output_file = 'processed_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nДанные успешно сохранены в файл: {output_file}")
    print(f"Обработано сообщений: {len(processed_data)}")
    print(f"Использовано аэропортов: {len(VALID_AIRPORTS)}")


if __name__ == "__main__":
    main()