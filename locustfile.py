from locust import HttpUser, SequentialTaskSet, task, between
from auth import AuthHelper
from client_payload_builder import *
import json
import time
import os
import logging
from datetime import datetime


# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
# Создаём папку logs, если её нет
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Формируем имя файла лога с путём к папке logs
log_filename = os.path.join(log_dir, f"locust_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Инициализируем логгер
log = logging.getLogger()

# Переопределяем print для использования логгера
print = log.info


class CargoScenario(SequentialTaskSet):
    def on_start(self):
        """Авторизация двух пользователей: API и обычного"""
        try:
            # Авторизация API-пользователя
            self.api_token = AuthHelper.login_as("api_user")
            if not self.api_token:
                print("❌ пользователю api_user не удалось авторизоваться")
                self.user.environment.runner.quit()
                return

            if not self.api_token.lower().startswith("bearer "):
                self.api_token = f"Bearer {self.api_token}"

            # Авторизация обычного пользователя
            self.default_token = AuthHelper.login_as("default_user")
            if not self.default_token:
                print("❌ пользователю default_user не удалось авторизоваться")
                self.user.environment.runner.quit()
                return

            if not self.default_token.lower().startswith("bearer "):
                self.default_token = f"Bearer {self.default_token}"

            # По умолчанию ставим API-токен
            self.client.headers.update({
                "Authorization": self.api_token,
                "Accept": "application/json",
                "Content-Type": "application/json"
            })

            print("✅ Авторизация прошла успешно — получены оба токена")

        except Exception as e:
            print(f"❌ Ошибка при авторизации пользователей: {e}")
            self.user.environment.runner.quit()

        # хранилище id грузомест по партиям
        self.all_ids = {
            "batch_1": [],
            "batch_2": [],
            "batch_3": [],
            "batch_4": []
        }

    def use_api_token(self):
        """Переключает авторизацию на API-пользователя"""
        self.client.headers["Authorization"] = self.api_token

    def use_default_token(self):
        """Переключает авторизацию на обычного пользователя"""
        self.client.headers["Authorization"] = self.default_token

    # ======== СОЗДАНИЕ ГРУЗОМЕСТ ========

    def save_ids(self):
        """Сохраняет все собранные id в JSON-файл"""
        with open("cargo_place_ids.json", "w", encoding="utf-8") as f:
            json.dump(self.all_ids, f, ensure_ascii=False, indent=2) # type: ignore[arg-type]

    def create_thousand(self, address_index, batch_name):
        """Создаёт 1000 успешных грузомест для указанного адреса"""
        self.use_api_token()
        success_count = 0
        attempts = 0
        max_attempts = 2000  # ограничение, чтобы избежать бесконечного цикла

        while success_count < 1000 and attempts < max_attempts:
            attempts += 1
            payload = CargoPlacePayloadBuilder.cargo_place_create()

            # подставляем нужный адрес доставки во все 5 элементов
            for j in range(5):
                payload["data"][j]["deliveryAddress"] = delivery_address[address_index]

            with self.client.post("/v1/api-ext/cargo-place/create-or-update-list",
                                  json=payload, catch_response=True) as response:
                if response.status_code == 200:
                    try:
                        resp = response.json()
                        ids = [item.get("id") for item in resp.get("data", []) if item.get("id")]
                        if ids:
                            self.all_ids[batch_name].extend(ids)
                            success_count += len(ids)
                            response.success()
                        else:
                            response.failure("Пустой список id в ответе")
                    except Exception as e:
                        response.failure(f"Ошибка парсинга ответа: {e}")
                else:
                    response.failure(f"Ошибка запроса: {response.status_code}")

            time.sleep(0.1)

            if success_count % 100 == 0 and success_count != 0:
                print(f"✅ {batch_name}: успешно создано {success_count} грузомест")

        self.save_ids()

        if success_count >= 1000:
            print(f"🎯 {batch_name} завершён — создано {success_count} грузомест")
            return True
        else:
            print(f"❌ {batch_name}: создано только {success_count} из 1000 — ошибка")
            return False

    @task
    def create_all_cargo_places(self):
        """Создаёт все 4000 грузомест последовательно"""
        results = []

        for i in range(4):
            batch_name = f"batch_{i + 1}"
            print(f"🚚 Создаём {i + 1}-ю тысячу грузомест...")
            success = self.create_thousand(i, batch_name)
            results.append(success)
            if not success:
                print(f"❌ Тест остановлен — не удалось создать {i + 1}-ю тысячу грузомест")
                self.user.environment.runner.quit()
                return  # прекращаем выполнение сценария

        if all(results):
            print("✅ Все 4000 грузомест успешно созданы!")
        else:
            failed = [f"{i + 1}-я" for i, ok in enumerate(results) if not ok]
            print(f"❌ Тест остановлен, не удалось создать {', '.join(failed)} тысячу(и) грузомест")
            self.user.environment.runner.quit()
            return


    # ======== ОБНОВЛЕНИЕ АДРЕСОВ И ПРОМЕЖУТОЧНЫЕ ПРОВЕРКИ ========

    def check_items_count(self, address_index, prefix=""):
        """Делает 2 запроса — по старому и новому адресу — и выводит itemsCount"""
        self.use_default_token()

        # старый адрес
        old_payload = CargoPlacePayloadBuilder.cargo_place_list_feature(address_index, use_new=False)
        resp_old = self.client.post("/v1/api/cargo-place/list/feature", json=old_payload)
        if resp_old.status_code == 200:
            count_old = resp_old.json().get("itemsCount", 0)
            print(f"{prefix}Старый адрес точки №{address_index + 1}: {count_old}")
        else:
            print(f"{prefix}Ошибка при запросе старого адреса ({resp_old.status_code})")

        # новый адрес
        new_payload = CargoPlacePayloadBuilder.cargo_place_list_feature(address_index, use_new=True)
        resp_new = self.client.post("/v1/api/cargo-place/list/feature", json=new_payload)
        if resp_new.status_code == 200:
            count_new = resp_new.json().get("itemsCount", 0)
            print(f"{prefix}Новый адрес точки №{address_index + 1}: {count_new}")
        else:
            print(f"{prefix}Ошибка при запросе нового адреса ({resp_new.status_code})")

    def update_and_check_point(self, address_index):
        """Обновляет адрес и делает проверки с интервалами"""
        self.use_api_token()

        # обновляем точку
        payload = CargoPlacePayloadBuilder.point_update(address_index)
        resp = self.client.post("/v1/api-ext/contractor-point/update", json=payload)

        if resp.status_code == 200:
            print(f"✅ Обновился адрес точки №{address_index + 1}")
        else:
            print(f"❌ Ошибка обновления точки №{address_index + 1}: {resp.status_code}")
            return False

        self.use_default_token()

        # через 5 секунд
        time.sleep(5)
        self.check_items_count(address_index)

        # через 10 секунд
        time.sleep(10)
        self.check_items_count(address_index, prefix="(прошло 10 секунд) ")

        # ещё через 10 секунд
        time.sleep(10)
        self.check_items_count(address_index, prefix="(прошло 20 секунд) ")

        return True

    @task
    def update_points(self):
        """Логика обновления 4 точек"""
        # первая точка
        print("🔄 Обновляем точку №1...")
        success_1 = self.update_and_check_point(0)
        if not success_1:
            print("❌ Тест остановлен — ошибка при обновлении точки №1")
            self.user.environment.runner.quit()
            return

        print("⏳ Ожидаем 10 секунд перед обновлением 2 и 3 точек...")
        time.sleep(10)

        # вторая и третья точки
        for idx in [1, 2]:
            print(f"🔄 Обновляем точку №{idx + 1}...")
            success = self.update_and_check_point(idx)
            if not success:
                print(f"❌ Тест остановлен — ошибка при обновлении точки №{idx + 1}")
                self.user.environment.runner.quit()
                return

        print("⏳ Ожидаем 10 секунд перед обновлением 4-й точки...")
        time.sleep(10)

        # четвёртая точка
        print("🔄 Обновляем точку №4...")
        success_4 = self.update_and_check_point(3)
        if not success_4:
            print("❌ Тест остановлен — ошибка при обновлении точки №4")
            self.user.environment.runner.quit()
            return

        print("⏳ Ожидаем 10 секунд перед запуском итоговых проверок...")
        time.sleep(10)

        # финальные проверки
        print("🚀 Запуск итоговых проверок...")
        self.final_check_all_points()

    # ======== МОНИТОРИНГ СПУСТЯ НЕСКОЛЬКО МИНУТ ========

    @task
    def final_check_all_points(self):
        """Через минуту после обновления всех точек делает итоговые проверки"""
        self.use_default_token()

        delays = [
            (30,  "1 минута"),
            (60,  "2 минуты"),
            (120, "4 минуты"),
            (180, "7 минут"),
            (240, "11 минут"),
            (300, "16 минут")
        ]

        for delay, label in delays:
            print(f"⏳ Ожидание {label} после обновления всех точек...")
            time.sleep(delay)

            print(f"\n📊 {label} после обновления всех точек:")

            all_ok = True  # флаг для финального сообщения

            for i in range(4):
                old_payload = CargoPlacePayloadBuilder.cargo_place_list_feature(i, use_new=False)
                new_payload = CargoPlacePayloadBuilder.cargo_place_list_feature(i, use_new=True)

                resp_old = self.client.post("/v1/api/cargo-place/list/feature", json=old_payload)
                resp_new = self.client.post("/v1/api/cargo-place/list/feature", json=new_payload)

                if resp_old.status_code == 200 and resp_new.status_code == 200:
                    count_old = resp_old.json().get("itemsCount", 0)
                    count_new = resp_new.json().get("itemsCount", 0)
                    print(
                        f"Старый адрес точки №{i + 1}: {count_old} | "
                        f"Новый адрес точки №{i + 1}: {count_new}"
                    )
                else:
                    all_ok = False
                    print(
                        f"❌ Ошибка при проверке точки №{i + 1}: "
                        f"{resp_old.status_code}/{resp_new.status_code}"
                    )

            # если это последняя итерация и всё ок
            if label == "16 минут" and all_ok:
                print("\n🏁 Итоговые проверки завершены — все адреса обработаны.")
                self.user.environment.runner.quit()


class ClientUser(HttpUser):
    tasks = [CargoScenario]
    host = AuthHelper.BASE_URL
    wait_time = between(2, 3)