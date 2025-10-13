from locust import HttpUser, SequentialTaskSet, task, between
from auth import AuthHelper
from client_payload_builder import *
import json
import time
import logging
from datetime import datetime


# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
log_filename = f"locust_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()
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

    def use_api_token(self):
        """Переключает авторизацию на API-пользователя"""
        self.client.headers["Authorization"] = self.api_token

    def use_default_token(self):
        """Переключает авторизацию на обычного пользователя"""
        self.client.headers["Authorization"] = self.default_token

        self.all_ids = {f"batch_{i}": [] for i in range(1, 5)}

    # def on_start(self):
    #     token = AuthHelper.login_as("api_client")
    #     if not token.lower().startswith("bearer "):
    #         token = f"Bearer {token}"
    #
    #     self.client.headers.update({
    #         "Authorization": token,
    #         "Accept": "application/json",
    #         "Content-Type": "application/json"
    #     })
    #     print("✅ Авторизация прошла успешно")
    #
    #     self.all_ids = {f"batch_{i}": [] for i in range(1, 5)}

    def save_ids(self):
        """Сохраняет все собранные id в JSON-файл"""
        with open("cargo_place_ids.json", "w", encoding="utf-8") as f:
            json.dump(self.all_ids, f, ensure_ascii=False, indent=4)

    # ======== ТАСКИ СОЗДАНИЯ ГРУЗОМЕСТ ========

    def create_thousand(self, address_index, batch_name):
        """Создаёт 1000 успешных грузомест для указанного адреса"""
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
                return  # прекращаем выполнение сценария

        if all(results):
            print("✅ Все 4000 грузомест успешно созданы!")
        else:
            failed = [f"{i + 1}-я" for i, ok in enumerate(results) if not ok]
            print(f"❌ Тест остановлен, не удалось создать {', '.join(failed)} тысячу(и) грузомест")


    # ======== ОБНОВЛЕНИЕ АДРЕСОВ И ПРОМЕЖУТОЧНЫЕ ПРОВЕРКИ ========

    def check_items_count(self, address_index, prefix=""):
        """Делает 2 запроса — по старому и новому адресу — и выводит itemsCount"""
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
        # обновляем точку
        payload = CargoPlacePayloadBuilder.point_update(address_index)
        resp = self.client.post("/v1/api-ext/point/update", json=payload)

        if resp.status_code == 200:
            print(f"✅ Обновился адрес точки №{address_index + 1}")
        else:
            print(f"❌ Ошибка обновления точки №{address_index + 1}: {resp.status_code}")
            return False

        # через 5 секунд
        time.sleep(5)
        self.check_items_count(address_index, prefix="")

        # через 10 секунд
        time.sleep(10)
        self.check_items_count(address_index, prefix="(прошло 10 секунд) ")

        # ещё через 10 секунд
        time.sleep(10)
        self.check_items_count(address_index, prefix="(прошло 20 секунд) ")

    @task
    def update_points(self):
        """Обновляет все 4 точки последовательно и выводит результат"""
        successful_updates = []

        for i in range(4):
            print(f"🔄 Обновляем точку №{i + 1}...")
            success = self.update_and_check_point(i)
            successful_updates.append(success)
            if not success:
                print(f"❌ Тест остановлен — ошибка при обновлении точки №{i + 1}")
                return  # прекращаем выполнение, если ошибка

        if all(successful_updates):
            print("🏁 Все точки успешно обновлены и проверены!")
        else:
            failed = [i + 1 for i, ok in enumerate(successful_updates) if not ok]
            print(f"❌ Не удалось обновить точки: {', '.join(map(str, failed))}")

    # ======== МОНИТОРИНГ СПУСТЯ НЕСКОЛЬКО МИНУТ ========

    @task
    def final_check_all_points(self):
        """Через 30 секунд после обновления всех точек делает итоговые проверки"""
        print("⏳ Ждём 30 секунд перед итоговой проверкой всех точек...")
        time.sleep(30)

        # 5 повторов: 1, 2, 3, 4 и 5 минут после обновления
        for minute in range(1, 6):
            print(f"\n🕐 {minute} минута после обновления всех точек:")
            for index in range(4):
                # старый адрес
                old_payload = CargoPlacePayloadBuilder.cargo_place_list_feature(index, use_new=False)
                resp_old = self.client.post("/v1/api/cargo-place/list/feature", json=old_payload)
                if resp_old.status_code == 200:
                    count_old = resp_old.json().get("itemsCount", 0)
                    print(f"Старый адрес точки №{index + 1} - {count_old}")
                else:
                    print(f"Ошибка при запросе старого адреса точки №{index + 1}: {resp_old.status_code}")

                # новый адрес
                new_payload = CargoPlacePayloadBuilder.cargo_place_list_feature(index, use_new=True)
                resp_new = self.client.post("/v1/api/cargo-place/list/feature", json=new_payload)
                if resp_new.status_code == 200:
                    count_new = resp_new.json().get("itemsCount", 0)
                    print(f"Новый адрес точки №{index + 1} - {count_new}")
                else:
                    print(f"Ошибка при запросе нового адреса точки №{index + 1}: {resp_new.status_code}")

            # ждём 60 секунд до следующей проверки
            if minute < 5:
                print("\n⏳ Ждём 60 секунд до следующей проверки...\n")
                time.sleep(60)

        print("🏁 Итоговые проверки завершены — все адреса обработаны.")


class ClientUser(HttpUser):
    tasks = [CargoScenario]
    host = AuthHelper.BASE_URL
    wait_time = between(1, 2)





# class ClientUser(HttpUser):
#     host = AuthHelper.BASE_URL
#     wait_time = between(1, 2)
#
#     def on_start(self):
#         token = AuthHelper.login_as("api_client")
#         self.client.headers.update({
#             "Authorization": token,
#             "Accept": "application/json",
#             "Content-Type": "application/json"
#         })
#
#         # структура для сохранения ID
#         self.all_id = {
#             "batch_1": [],
#             "batch_2": [],
#             "batch_3": [],
#             "batch_4": []
#         }
#
#     def save_id_to_file(self):
#         """Сохраняет собранные ID в json файл"""
#         with open("cargo_place_id.json", "w", encoding="utf-8") as f:
#             json.dump(self.all_id, f, ensure_ascii=False, indent=4) # type: ignore[arg-type]
#
#     def create_thousand_cargo_places(self, address_index, batch_name):
#         """Создаёт 1000 грузомест для заданного адреса и сохраняет их id"""
#         for i in range(1000):
#             payload = CargoPlacePayloadBuilder.cargo_place_create()
#             # Подставляем конкретный адрес доставки
#             payload["data"][0]["deliveryAddress"] = delivery_address[address_index]
#             payload["data"][1]["deliveryAddress"] = delivery_address[address_index]
#             payload["data"][2]["deliveryAddress"] = delivery_address[address_index]
#             payload["data"][3]["deliveryAddress"] = delivery_address[address_index]
#             payload["data"][4]["deliveryAddress"] = delivery_address[address_index]
#
#             with self.client.post("/v1/api-ext/cargo-place/create-or-update-list",
#                                   json=payload, catch_response=True) as response:
#                 if response.status_code == 200:
#                     try:
#                         resp_json = response.json()
#                         # собираем все id из data
#                         ids = [item.get("id") for item in resp_json.get("data", []) if item.get("id")]
#                         self.all_id[batch_name].extend(ids)
#                     except Exception as e:
#                         response.failure(f"Ошибка парсинга ответа: {e}")
#                 else:
#                     response.failure(f"Ошибка запроса: {response.status_code}")
#
#             # пауза, чтобы не перегружать API
#             time.sleep(1)
#
#         # сохраняем промежуточный результат посел 1000 созданных ГМ
#         self.save_id_to_file()
#
#     @task
#     def task_1(self):
#         self.create_thousand_cargo_places(0, "batch_1")
#
#     @task
#     def task_2(self):
#         self.create_thousand_cargo_places(1, "batch_2")
#
#     @task
#     def task_3(self):
#         self.create_thousand_cargo_places(2, "batch_3")
#
#     @task
#     def task_4(self):
#         self.create_thousand_cargo_places(3, "batch_4")



