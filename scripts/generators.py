import random

from faker import Faker
from transliterate import translit
from faker.providers import BaseProvider
from faker_airtravel import AirTravelProvider

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
    
    def passenger_name(self):
        # Генерация ФИО с разными форматами написания
        ru_fake = Faker('ru_RU')
        en_fake = Faker('en')
        
        is_male = random.choice([True, False])
        
        if is_male:
            ru_first = ru_fake.first_name_male()
            ru_last = ru_fake.last_name_male()
            ru_middle = ru_fake.middle_name_male()   
        else:
            ru_first = ru_fake.first_name_female()
            ru_last = ru_fake.last_name_female()
            ru_middle = ru_fake.middle_name_female()
        
        random_value = random.random()
    
        if random_value < 0.7:
            # 70% - русское имя (разные форматы)
            formats = [
                # Полное ФИО
                f"{ru_last} {ru_first} {ru_middle}",      # Иванов Сергей Иванович
                f"{ru_first} {ru_middle} {ru_last}",      # Сергей Иванович Иванов
            
                # С инициалами
                # f"{ru_last} {ru_first[0]}. {ru_middle[0]}.",  # Иванов С.И.
                # f"{ru_first[0]}. {ru_middle[0]}. {ru_last}",  # С.И. Иванов
                # f"{ru_first} {ru_last[0]}.{ru_middle[0]}.",   # Сергей И.И.
            
                # Без отчества (для краткости)
                f"{ru_first} {ru_last}",                      # Сергей Иванов
                f"{ru_last} {ru_first}",                      # Иванов Сергей
                # f"{ru_first[0]}. {ru_last}",                  # С. Иванов
            ]
            return random.choice(formats)

    
        elif random_value < 0.9:
            # 20% - транслитерация (разные форматы)
            en_first = translit(ru_first, 'ru', reversed=True)
            en_last = translit(ru_last, 'ru', reversed=True)
            en_middle = translit(ru_middle, 'ru', reversed=True)
        
            formats = [
                # Полное ФИО
                f"{en_last} {en_first} {en_middle}",      # Иванов Сергей Иванович
                f"{en_first} {en_middle} {en_last}",      # Сергей Иванович Иванов
            
                # С инициалами
                # f"{en_last} {en_first[0]}. {en_middle[0]}.",  # Иванов С.И.
                # f"{en_first[0]}. {en_middle[0]}. {en_last}",  # С.И. Иванов
                # f"{en_first} {en_last[0]}.{en_middle[0]}.",   # Сергей И.И.
            
                # Без отчества (для краткости)
                f"{en_first} {en_last}",                      # Сергей Иванов
                f"{en_last} {en_first}",                      # Иванов Сергей
                # f"{en_first[0]}. {en_last}",                  # С. Иванов
                
                # Смешанный формат
                f"{ru_first} {ru_last} / {en_first} {en_last}",  # Сергей Иванов / Sergei Ivanov
                f"{ru_last} {ru_first} {ru_middle} ({en_last} {en_first} {en_middle})"  # Иванов Сергей Иванович (Ivanov Sergei Ivanovich)
            ]
            return random.choice(formats)
    
        else:
            # 10% - английское имя (разные форматы)
            en_first = en_fake.first_name()
            en_last = en_fake.last_name()
        
            formats = [
                f"{en_first} {en_last}",           # John Smith
                f"{en_last} {en_first}",           # Smith John
                # f"{en_first[0]}. {en_last}",       # J. Smith
                f"{en_last}, {en_first}",          # Smith, John
            #    f"{en_first} {en_last} Jr.",
            #    f"{en_first} {en_last} Sr."
            ]
            return random.choice(formats)

class AviationDocumentsProvider(BaseProvider):
    """Провайдер для авиационных документов"""
    
    def ticket_number(self):
        """Генерация номера авиабилета"""
        airline_codes = ['421']   #, '555', '262', '124']  S7, SU, U6, AC
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"
        
        formats = [
            # f"{airline} {number}",            421 1234567890
            f"{airline}{number}",             # 4211234567890
            # f"{airline}-{number}",            421-1234567890
            # f"{airline} {number[:4]} {number[4:]}",  421 1234 567890
            f"билет {airline}{number}",     # билет 4211234567890
            f"номер билета {airline}{number}"
        ]
        return random.choice(formats)
    
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
            f"бронирование {pnr}"
        ]
        return random.choice(formats)
    
    def boarding_pass(self): # Нужен ли?
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
                f"посадочный талон {number}"
            ]
            return random.choice(formats)
    
    def emd_number(self): # Нужен ли?
        """Генерация номера EMD (Electronic Miscellaneous Document)"""
        airline_codes = ['421'] #, '555', '262']
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"
        
        formats = [
            f"{airline} {number}",          # 421 1234567890
            f"EMD {airline} {number}",      # EMD 421 1234567890
            f"{airline}{number}",           # 4211234567890
            f"документ EMD {airline} {number}",
            f"номер EMD {airline} {number}"
        ]
        return random.choice(formats)
    
    def order_number(self):
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # только заглавные буквы и цифры
    
        # Генерируем строку из 7 случайных символов
        random_chars = ''.join(random.choices(characters, k=7))
        
        formats = [
            random_chars,                                      # DRE5TW6
            f"ORD{random_chars}",                             # ORDDRE5TW6
            f"ORDER-{random_chars}",                          # ORDER-DRE5TW6
            f"ЗАКАЗ{random_chars}",                           # ЗАКАЗDRE5TW6
            f"№{random_chars}",                               # №DRE5TW6
            f"заказ №{random_chars}",                         # заказ №DRE5TW6
            f"{random_chars[:3]}-{random_chars[3:]}",         # DRE-5TW6
            f"{random_chars[:2]}{random_chars[2:4]}{random_chars[4:]}",  # DR E5 TW6 (без пробелов)
        ]
        return random.choice(formats)
    
    def ffp_number(self):
        s7_number = f"{self.random_int(100000000, 999999999)}"  # 100025756
    
        # Различные текстовые форматы для S7
        formats = [
            # Просто номер
            s7_number,
        
            # С префиксом S7
            f"S7{s7_number}",
            f"S7 {s7_number}",
            f"S7-{s7_number}",
            
            # С обозначением программы
            f"S7 Priority {s7_number}",
            f"S7 Приоритет {s7_number}",
            f"Приоритет {s7_number}",
            f"Priority {s7_number}",
        
            # С текстом "бонусная карта"
            f"бонусная карта {s7_number}",
            f"бонусная карта S7 {s7_number}",
            f"карта S7 {s7_number}",

            # С текстом "номер программы"
            f"номер программы {s7_number}",
            f"номер бонусной программы {s7_number}",
            f"бонусная программа {s7_number}",

            # С FFP обозначением
            f"FFP {s7_number}",
            f"FFP S7 {s7_number}",
            f"номер FFP {s7_number}",

            # С разделителями в номере
            f"{s7_number[:3]} {s7_number[3:6]} {s7_number[6:]}",  # 100 025 756
            f"{s7_number[:3]}-{s7_number[3:6]}-{s7_number[6:]}",  # 100-025-756

            # Комбинированные форматы
            f"S7 Приоритет {s7_number[:3]} {s7_number[3:6]} {s7_number[6:]}",
            f"бонусная карта S7 {s7_number[:3]}-{s7_number[3:6]}-{s7_number[6:]}",
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
        airlines = ['S7 Airlines', 'Аэрофлот', 'Уральские авиалинии', 'Победа', 'Ютейр', 'Россия']
        return random.choice(airlines)
    
    # def russian_airport_iata(self):
    #     """Российские аэропорты с кодами IATA"""
    #     airports = ['SVO', 'DME', 'VKO', 'LED', 'KRR', 'OVB', 'KJA', 'AER', 'ROV', 'KGD', 'MRV', 'GOJ']
    #     return random.choice(airports)
    
    def russian_flight_number(self):
        """Номера рейсов российских авиакомпаний"""
        airlines = ['S7', 'SU', 'U6', 'DP', '5N', 'WZ', 'FV']
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
    
    def passenger_name(self):
        return self.documents_provider.passenger_name()
    
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
    
    def ffp_number(self):
        return self.aviation_provider.ffp_number()
    
# Утилиты для удобного импорта
def setup_faker_providers(faker_instance):
    """Настройка всех провайдеров для Faker instance"""
    faker_instance.add_provider(AirTravelProvider)
    faker_instance.add_provider(RussianAviationProvider)
    return faker_instance

def get_all_document_types():
    """Возвращает список всех типов документов"""
    return [
        'INTERNATIONAL_PASSPORT', 
        'BIRTH_CERTIFICATE',
        'VISA',
        'TICKET_NUMBER',
        'BOOKING_REF',
        'BOARDING_PASS',
        'EMD_NUMBER',
        'ORDER_NUMBER',
        'FFP_NUMBER'
    ]