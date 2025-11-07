import random
import re
from faker import Faker
from faker.providers import BaseProvider

class RussianDocumentsProvider(BaseProvider):
    """Провайдер для российских документов"""
    
    def international_passport(self):
        """Генерация номера загранпаспорта"""
        series = random.choice(['53', '60', '61', '62', '63', '64', '65', '70', '71', '72'])
        number = f"{self.random_int(1000000, 9999999)}"
        
        formats = [
            f"{series} {number}",           # 65 1234567
            f"{series}{number}",            # 651234567
            f"{series}-{number}",           # 65-1234567
            f"серия {series} номер {number}", # серия 65 номер 1234567
            f"загранпаспорт {series} {number}" # с указанием документа
        ]
        return random.choice(formats)
    
    def birth_certificate(self):
        """Генерация номера свидетельства о рождении"""
        roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        letters = ['ЕР', 'МС', 'АВ', 'СР', 'ТУ', 'НР', 'КЕ', 'МР']
        number = f"{self.random_int(100000, 999999)}"
        
        formats = [
            f"{random.choice(roman_numerals)}-{random.choice(letters)} № {number}", # II-ЕР № 123456
            f"{random.choice(roman_numerals)}-{random.choice(letters)} {number}",   # II-ЕР 123456
            f"{random.choice(roman_numerals)}-{random.choice(letters)}№{number}",   # II-ЕР№123456
            f"{random.choice(roman_numerals)}-{random.choice(letters)}.№{number}",  # II-ЕР.№123456
            f"свидетельство {random.choice(roman_numerals)}-{random.choice(letters)} № {number}" # с текстом
        ]
        return random.choice(formats)
    
    def visa(self):
        """Генерация номера визы"""
        # Шенгенская виза
        if random.random() > 0.5:
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            visa_number = ''.join(random.choices(chars, k=9))
            formats = [
                visa_number,
                f"{visa_number[:3]} {visa_number[3:6]} {visa_number[6:]}",  # A12 345 67B
                f"{visa_number[:3]}-{visa_number[3:6]}-{visa_number[6:]}",  # A12-345-67B
                f"виза № {visa_number}"
            ]
        else:
            # Американская/другие визы
            visa_number = f"{self.random_int(10000000, 99999999)}"
            formats = [visa_number, f"виза № {visa_number}"]
        
        return random.choice(formats)

class AviationDocumentsProvider(BaseProvider):
    """Провайдер для авиационных документов"""
    
    def ticket_number(self):
        """Генерация номера авиабилета"""
        airline_codes = ['421', '555', '262', '124']  # S7, SU, U6, AC
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"
        return f"{airline}{number}"
    
    def booking_ref(self):
        """Генерация номера бронирования (PNR)"""
        chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'  # без I, O, Q
        pnr = ''.join(random.choices(chars, k=6))
        
        formats = [
            pnr,
            f"{pnr[:3]}-{pnr[3:]}",        # ABC-123
            f"бронь {pnr}",                 # бронь ABC123
            f"PNR {pnr}",                   # PNR ABC123
            f"код {pnr}",                   # код ABC123
            f"номер брони {pnr}",
            f"бронирование {pnr}",
            f"резерв {pnr}",
            f"код бронирования {pnr}",
            f"номер резервации {pnr}",
            f"confirm {pnr}",
            f"confirm-{pnr}"
        ]
        return random.choice(formats)
    
    def boarding_pass(self):
        """Генерация номера посадочного талона"""
        # 50% chance что будет как PNR, 50% - отдельный номер
        if random.random() > 0.5:
            return self.booking_ref()
        else:
            number = f"{self.random_int(1000000000, 9999999999999)}"
            formats = [
                number,
                f"посадочный {number}",
                f"талон {number}",
                f"BP{number}",              # Boarding Pass
                f"посадочный талон {number}",
                f"номер посадки {number}",
                f"билет на посадку {number}",
                f"boarding pass {number}",
                f"boarding-{number}",
                f"BP № {number}",
                f"посадка № {number}"
            ]
            return random.choice(formats)
    
    def emd_number(self):
        """Генерация номера EMD (Electronic Miscellaneous Document)"""
        airline_codes = ['421', '555', '262']
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"
        
        formats = [
            f"{airline} {number}",          # 421 1234567890
            f"EMD {airline} {number}",      # EMD 421 1234567890
            f"{airline}{number}",           # 4211234567890
            f"документ EMD {airline} {number}",
            f"номер EMD {airline} {number}",
            f"электронный документ {airline} {number}",
            f"EMD-документ {number}",
            f"EMD № {number}",
            f"электронный билет {airline} {number}",
            f"MCO {airline} {number}"
        ]
        return random.choice(formats)
    
    def order_number(self):
        """Генерация номера заказа"""
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # только заглавные буквы и цифры
        random_chars = ''.join(random.choices(characters, k=7))
        
        formats = [
            random_chars,                                      # DRE5TW6
            f"ORD{random_chars}",                             # ORDDRE5TW6
            f"ORDER-{random_chars}",                          # ORDER-DRE5TW6
            f"ЗАКАЗ{random_chars}",                           # ЗАКАЗDRE5TW6
            f"№{random_chars}",                               # №DRE5TW6
            f"заказ №{random_chars}",                         # заказ №DRE5TW6
            f"{random_chars[:3]}-{random_chars[3:]}",         # DRE-5TW6
            f"{random_chars[:2]}-{random_chars[2:4]}-{random_chars[4:]}", # DR-E5-TW6
            f"ORD-{random_chars}",
            f"order-{random_chars}",
            f"ORD №{random_chars}",
            f"заказ-{random_chars}",
            f"ORDER {random_chars}",
            f"ордер {random_chars}",
            f"ордер №{random_chars}"
        ]
        return random.choice(formats)

class RussianAviationProvider(BaseProvider):
    """Комплексный провайдер для российских авиационных данных"""
    
    def __init__(self, generator):
        super().__init__(generator)
        self.documents_provider = RussianDocumentsProvider(generator)
        self.aviation_provider = AviationDocumentsProvider(generator)
    
    def russian_airline(self):
        """Российские авиакомпании"""
        airlines = ['S7 Airlines', 'Аэрофлот', 'Уральские авиалинии', 'Победа', 'Ютейр', 'Россия', 'Nordwind', 'Smartavia', 'Red Wings', 'Azur Air']
        return random.choice(airlines)
    
    def russian_flight_number(self):
        """Номера рейсов российских авиакомпаний"""
        airlines = ['S7', 'SU', 'U6', 'DP', '5N', 'WZ', 'FV', 'ND', 'SM', 'RW', 'ZF']
        airline = random.choice(airlines)
        number = self.random_int(1, 9999)
        return f"{airline}{number}"
    
    # Делегирование методов документов для удобства
    def international_passport(self):
        return self.documents_provider.international_passport()
    
    def birth_certificate(self):
        return self.documents_provider.birth_certificate()
    
    def visa(self):
        return self.documents_provider.visa()
    
    def ticket_number(self):
        return self.aviation_provider.ticket_number()
    
    def booking_ref(self):
        return self.aviation_provider.booking_ref()
    
    def boarding_pass(self):
        return self.aviation_provider.boarding_pass()
    
    def emd_number(self):
        return self.aviation_provider.emd_number()
    
    def order_number(self):
        return self.aviation_provider.order_number()

def setup_faker_providers(faker_instance):
    """Настройка всех провайдеров для Faker instance"""
    try:
        from faker_airtravel import AirTravelProvider
        faker_instance.add_provider(AirTravelProvider)
    except ImportError:
        pass  # Если библиотека не установлена, пропускаем
    
    faker_instance.add_provider(RussianAviationProvider)
    return faker_instance

# ====================== ФУНКЦИИ ГЕНЕРАЦИИ ДАННЫХ ======================

fake = Faker(locale='ru_RU')
fake = setup_faker_providers(fake)

# Список поддерживаемых тегов
TAGS = [
    'PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'CITY', 'COUNTRY', 'TIME', 'DATE',
    'INTERNATIONAL', 'TICKET_NUMBER', 'ORDER_NUMBER', 'BOOKING_REF', 'BOARDING_PASS', 
    'EMD_NUMBER', 'BIRTH_CERTIFICATE', 'VISA', 'FLIGHT', 'AIRLINE', 'SEAT'
]

# Словарь функций генерации данных для каждого тега
DATAGEN = {
    'PHONE': lambda: fake.phone_number(),
    'PASSPORT': lambda: fake.passport_number(),
    'NAME': lambda: fake.name(),
    'DOB': lambda: str(fake.date_of_birth(minimum_age=18, maximum_age=90)),
    'EMAIL': lambda: fake.email(),
    'CITY': lambda: fake.city_name(),
    'COUNTRY': lambda: fake.country(),
    'TIME': lambda: fake.time(),
    'DATE': lambda: fake.date(),
    'INTERNATIONAL': lambda: fake.international_passport(),
    'TICKET_NUMBER': lambda: fake.ticket_number(),
    'ORDER_NUMBER': lambda: fake.order_number(),
    'BOOKING_REF': lambda: fake.booking_ref(),
    'BOARDING_PASS': lambda: fake.boarding_pass(),
    'EMD_NUMBER': lambda: fake.emd_number(),
    'BIRTH_CERTIFICATE': lambda: fake.birth_certificate(),
    'VISA': lambda: fake.visa(),
    'FLIGHT': lambda: f"{random.choice(['SU', 'AF', 'LH', 'TK', 'BA', 'AY', 'S7', 'U6', 'DP', '5N'])}{random.randint(100, 9999)}",
    'AIRLINE': lambda: fake.russian_airline(),
    'SEAT': lambda: f"{random.choice(['1A', '2B', '3C', '4D', '5E', '6F', '7A', '8B', '9C', '10D', '11E', '12F', '13A', '14B', '15C'])}"
}

def replace_and_label(message):
    """
    Заменяет теги в сообщении на реальные данные и создает разметку сущностей
    
    Args:
        message (str): Исходное сообщение с тегами
    
    Returns:
        dict: Словарь с текстом и разметкой сущностей
    """
    obj = {
        'text': message,
        'entities': []
    }

    tmp_entities = {}  # Временное хранилище для сгенерированных данных и их тегов

    # Заменяем каждый тег на сгенерированные данные
    for tag in TAGS:
        if tag in obj['text']:
            # Генерируем данные для этого тега
            generated_data = str(DATAGEN[tag]())
            
            # Сохраняем позиции всех вхождений тега
            start_pos = 0
            while True:
                start_idx = obj['text'].find(tag, start_pos)
                if start_idx == -1:
                    break
                
                # Заменяем тег на сгенерированные данные
                end_idx = start_idx + len(tag)
                new_text = obj['text'][:start_idx] + generated_data + obj['text'][end_idx:]
                
                # Обновляем позиции для всех существующих сущностей
                for i, (ent_start, ent_end, ent_label) in enumerate(obj['entities']):
                    if ent_start > start_idx:
                        # Сдвигаем позиции сущностей после замены
                        length_diff = len(generated_data) - len(tag)
                        obj['entities'][i] = [ent_start + length_diff, ent_end + length_diff, ent_label]
                
                # Добавляем новую сущность
                entity_start = start_idx
                entity_end = start_idx + len(generated_data)
                obj['entities'].append([entity_start, entity_end, tag])
                
                # Обновляем текст и позицию для поиска следующего вхождения
                obj['text'] = new_text
                start_pos = entity_end  # Продолжаем поиск после вставленного текста
    
    # Сортируем сущности по позиции начала
    obj['entities'].sort(key=lambda x: x[0])
    
    return obj