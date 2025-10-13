from faker import Faker
from datetime import datetime as dt, timezone, timedelta
import random

faker = Faker("ru_RU")


class CargoPlaceData:
    @staticmethod
    def bar_code():
        russian_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        letters = ''.join(random.choices(russian_letters, k=4))
        digits = ''.join(random.choices('0123456789', k=13))
        result = f"{letters}_{digits}"
        return result

    @staticmethod
    def external_id():
        return random.randint(10 ** 11, 10 ** 12 - 1)

    @staticmethod
    def name_cargo_place():
        return faker.word()

    @staticmethod
    def external_address():
        return faker.address()

    @staticmethod
    def time_iso():
        now = dt.now(timezone.utc)

        date_minus_10 = now - timedelta(days=10)
        date_plus_10 = now + timedelta(days=10)
        date_plus_20 = now + timedelta(days=20)

        def format_to_iso(d):
            return d.strftime('%Y-%m-%dT%H:%M:%S') + f'.{int(d.microsecond / 1000):03d}Z'

        return format_to_iso(date_minus_10), format_to_iso(date_plus_10), format_to_iso(date_plus_20)