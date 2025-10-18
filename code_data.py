print('code_data')

from faker import Faker
import pandas as pd
import random
import os
import json
from datetime import datetime, timedelta

fake = Faker(locale='ru_RU')

# Загрузка данных аэропортов с улучшенной обработкой
try:
    df = pd.read_csv(os.path.join('data', 'Airports.csv'))
    print("Столбцы в Airports.csv:", df.columns.tolist())
    
    # Найдем подходящие столбцы для аэропортов
    airport_columns = []
    possible_airport_columns = ['Название аэропорта', 'Аэропорт', 'Airport', 'Airport Name', 'Name', 
                               'аэропорт', 'Название', 'AIRPORT', 'AIRPORT_NAME']
    
    for col in df.columns:
        if any(possible in col for possible in possible_airport_columns):
            airport_columns.append(col)
    
    # Если не нашли специальных столбцов, используем все столбцы
    if not airport_columns:
        airport_columns = df.columns.tolist()
        print(f"Специальные столбцы для аэропортов не найдены, используем все: {airport_columns}")
    else:
        print(f"Найдены столбцы для аэропортов: {airport_columns}")
        
except Exception as e:
    print(f"Ошибка загрузки Airports.csv: {e}, создаем заглушку")
    df = pd.DataFrame({
        'Airport': ['Шереметьево', 'Домодедово', 'Внуково', 'Пулково'],
        'IATA': ['SVO', 'DME', 'VKO', 'LED']
    })
    airport_columns = ['Airport']

TAGS = ['PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'AIRPORT', 'CITY', 'COUNTRY', 'FLIGHT', 'TIME', 'DATE', 
        'FLIGHT_NUMBER', 'TICKET_NUMBER', 'SEAT_NUMBER', 'ORDER_NUMBER', 'DOCUMENT_TYPE', 'TIMEZONE', 
        'FROM_LOCATION', 'TO_LOCATION', 'DEPARTURE_DATE', 'ARRIVAL_DATE', 'TRANSFERS', 'CLASS', 'AIRLINE', 'BAGGAGE']

DATAGEN = {
    'PHONE': fake.phone_number,
    'PASSPORT': fake.passport_number,
    'NAME': fake.name,
    'DOB': fake.date_of_birth,
    'EMAIL': fake.email,
    'AIRPORT': lambda: random.choice(df[random.choice(airport_columns)].dropna()) if not df.empty else random.choice(['Шереметьево', 'Домодедово', 'Внуково', 'Пулково']),
    'FLIGHT': lambda: 'NONE',
    'CITY': fake.city_name,
    'TIME': fake.time,
    'DATE': fake.date,
    # Новые теги:
    'FLIGHT_NUMBER': lambda: f"{random.choice(['SU', 'AF', 'LH', 'TK', 'BA', 'AY'])}{random.randint(100, 9999)}",
    'TICKET_NUMBER': lambda: ''.join([str(random.randint(0, 9)) for _ in range(13)]),
    'SEAT_NUMBER': lambda: f"{random.randint(1, 60)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
    'ORDER_NUMBER': lambda: f"ORD{random.randint(100000, 999999)}",
    'DOCUMENT_TYPE': lambda: random.choice(['Паспорт РФ', 'Загранпаспорт', 'Свидетельство о рождении', 'Удостоверение личности', 'Вид на жительство в РФ']),
    'TIMEZONE': lambda: random.choice([f"+{i}" for i in range(1, 13)] + [f"-{i}" for i in range(1, 13)]),
    'FROM_LOCATION': fake.city_name,
    'TO_LOCATION': fake.city_name,
    'DEPARTURE_DATE': lambda: (datetime.now() + timedelta(days=random.randint(1, 365))).strftime("%d.%m.%Y"),
    'ARRIVAL_DATE': lambda: (datetime.now() + timedelta(days=random.randint(2, 370))).strftime("%d.%m.%Y"),
    'TRANSFERS': lambda: str(random.randint(0, 3)),
    'CLASS': lambda: random.choice(['Эконом', 'Бизнес', 'Первый']),
    'AIRLINE': lambda: random.choice(['Аэрофлот', 'S7 Airlines', 'Уральские авиалинии', 'Победа', 'Red Wings']),
    'BAGGAGE': lambda: random.choice(['1 багаж', '2 багажа', 'ручная кладь'])
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
    
    # Обрабатываем все сообщения
    processed_data = []
    for i, message in enumerate(messages, 1):
        result = replaceAndLabel(message)
        processed_data.append(result)
        print(f"Обработано сообщение {i}/{len(messages)}")
    
    # Сохраняем в JSON файл
    output_file = 'processed_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nДанные успешно сохранены в файл: {output_file}")
    print(f"Обработано сообщений: {len(processed_data)}")


if __name__ == "__main__":
    main()