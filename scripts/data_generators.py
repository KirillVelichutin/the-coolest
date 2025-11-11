import random
from faker import Faker
from faker.providers import BaseProvider

fake = Faker(locale='ru_RU')

class RussianDocumentsProvider(BaseProvider):
    def international_passport(self):
        series = random.choice(['53', '60', '61', '62', '63', '64', '65'])
        number = f"{self.random_int(1000000, 9999999)}"
        return random.choice([f"{series} {number}", f"{series}-{number}", f"загранпаспорт {series} {number}"])
    
    def birth_certificate(self):
        roman = random.choice(['I', 'II', 'III', 'IV', 'V'])
        letter = random.choice(['ЕР', 'МС', 'АВ', 'СР'])
        number = f"{self.random_int(100000, 999999)}"
        return f"{roman}-{letter} № {number}"
    
    def visa(self):
        if random.random() > 0.5:
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            visa_num = ''.join(random.choices(chars, k=9))
            return f"виза № {visa_num}"
        else:
            visa_num = f"{self.random_int(10000000, 99999999)}"
            return f"виза № {visa_num}"

class AviationProvider(BaseProvider):
    def ticket_number(self):
        airline = random.choice(['421', '555', '262'])
        number = f"{self.random_int(1000000000, 9999999999)}"
        return f"{airline}{number}"
    
    def booking_ref(self):
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789'
        pnr = ''.join(random.choices(chars, k=6))
        return random.choice([pnr, f"бронь {pnr}", f"PNR {pnr}"])
    
    def boarding_pass(self):
        if random.random() > 0.5:
            return self.booking_ref()
        number = f"{self.random_int(1000000000, 9999999999)}"
        return random.choice([number, f"посадочный {number}", f"BP{number}"])
    
    def emd_number(self):
        airline = random.choice(['421', '555'])
        number = f"{self.random_int(1000000000, 9999999999)}"
        return random.choice([f"EMD {airline} {number}", f"документ EMD {airline} {number}"])
    
    def order_number(self):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        rand = ''.join(random.choices(chars, k=7))
        return random.choice([rand, f"ORDER-{rand}", f"ЗАКАЗ{rand}"])
    
    def russian_airline(self):
        airlines = ['S7 Airlines', 'Аэрофлот', 'Уральские авиалинии', 'Победа']
        return random.choice(airlines)

fake.add_provider(RussianDocumentsProvider)
fake.add_provider(AviationProvider)

TAGS = ['PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'CITY', 'COUNTRY', 'TIME', 'DATE',
        'INTERNATIONAL', 'TICKET_NUMBER', 'ORDER_NUMBER', 'BOOKING_REF', 'BOARDING_PASS',
        'EMD_NUMBER', 'BIRTH_CERTIFICATE', 'VISA', 'FLIGHT', 'AIRLINE', 'SEAT']

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
    'FLIGHT': lambda: f"{random.choice(['SU', 'S7', 'U6', 'DP'])}{random.randint(100, 9999)}",
    'AIRLINE': lambda: fake.russian_airline(),
    'SEAT': lambda: random.choice(['1A', '2B', '3C', '4D', '5E', '6F', '7A', '8B', '9C', '10D'])
}

def replace_and_label(message):
    obj = {'text': message, 'entities': []}
    
    for tag in TAGS:
        if tag in obj['text']:
            generated_data = str(DATAGEN[tag]())
            start_idx = obj['text'].find(tag)
            end_idx = start_idx + len(tag)
            new_text = obj['text'][:start_idx] + generated_data + obj['text'][end_idx:]
            obj['text'] = new_text
            obj['entities'].append([start_idx, start_idx + len(generated_data), tag])
    
    obj['entities'].sort(key=lambda x: x[0])
    return obj