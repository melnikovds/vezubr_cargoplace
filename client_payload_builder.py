from client_data_generator import *
from datetime import date

departure_address = 25519
delivery_address = [25515, 25516, 25517, 25518]


class CargoPlacePayloadBuilder:
    @staticmethod
    def cargo_place_create():
        return {
            "data": [
                {
                    "parentId": None,
                    "barCode": CargoPlaceData.bar_code(),
                    "type": "free",
                    "sealNumber": "Пломба 1",
                    "wmsNumber": "Номер ВМС 1",
                    "category": 1,
                    "quantity": 10,
                    "requiredSentAt": CargoPlaceData.time_iso()[1],
                    "requiredDeliveredAt": CargoPlaceData.time_iso()[2],
                    "length": 1000,
                    "width": 1000,
                    "height": 1000,
                    "volume": 1500000,
                    "weight": 1500,
                    "reverseCargoType": None,
                    "reverseCargoReason": None,
                    "comment": None,
                    "invoiceNumber": "Накладная_замена1",
                    "invoiceDate": CargoPlaceData.time_iso()[0],
                    "innShipper": "5009112893",
                    "kppShipper": "500901001",
                    "innConsignee": "9705207762",
                    "kppConsignee": "770501001",
                    "cost": 10000,
                    "totalCost": 12000,
                    "departureAddressExternalId": None,
                    "departureAddress": departure_address,
                    "deliveryAddress": delivery_address,
                    "title": CargoPlaceData.name_cargo_place(),
                    "status": "new",
                    "statusAddressExternalId": None,
                    "externalId": None,
                    "isPlanned": True
                },
                {
                    "parentId": None,
                    "barCode": CargoPlaceData.bar_code(),
                    "type": "free",
                    "sealNumber": "Пломба 2",
                    "wmsNumber": "Номер ВМС 2",
                    "category": 1,
                    "quantity": 20,
                    "requiredSentAt": CargoPlaceData.time_iso()[1],
                    "requiredDeliveredAt": CargoPlaceData.time_iso()[2],
                    "length": 1000,
                    "width": 1000,
                    "height": 1000,
                    "volume": 2500000,
                    "weight": 2500,
                    "reverseCargoType": None,
                    "reverseCargoReason": None,
                    "comment": None,
                    "invoiceNumber": "Накладная_замена2",
                    "invoiceDate": CargoPlaceData.time_iso()[0],
                    "innShipper": "5009112893",
                    "kppShipper": "500901001",
                    "innConsignee": "9705207762",
                    "kppConsignee": "770501001",
                    "cost": 20000,
                    "totalCost": 22000,
                    "departureAddressExternalId": None,
                    "departureAddress": departure_address,
                    "deliveryAddress": delivery_address,
                    "title": CargoPlaceData.name_cargo_place(),
                    "status": "new",
                    "statusAddressExternalId": None,
                    "externalId": None,
                    "isPlanned": True
                },
                {
                    "parentId": None,
                    "barCode": CargoPlaceData.bar_code(),
                    "type": "free",
                    "sealNumber": "Пломба 3",
                    "wmsNumber": "Номер ВМС 3",
                    "category": 1,
                    "quantity": 30,
                    "requiredSentAt": CargoPlaceData.time_iso()[1],
                    "requiredDeliveredAt": CargoPlaceData.time_iso()[2],
                    "length": 1000,
                    "width": 1000,
                    "height": 1000,
                    "volume": 3500000,
                    "weight": 3500,
                    "reverseCargoType": None,
                    "reverseCargoReason": None,
                    "comment": None,
                    "invoiceNumber": "Накладная_замена3",
                    "invoiceDate": CargoPlaceData.time_iso()[0],
                    "innShipper": "5009112893",
                    "kppShipper": "500901001",
                    "innConsignee": "9705207762",
                    "kppConsignee": "770501001",
                    "cost": 30000,
                    "totalCost": 32000,
                    "departureAddressExternalId": None,
                    "departureAddress": departure_address,
                    "deliveryAddress": delivery_address,
                    "title": CargoPlaceData.name_cargo_place(),
                    "status": "new",
                    "statusAddressExternalId": None,
                    "externalId": None,
                    "isPlanned": True
                },
                {
                    "parentId": None,
                    "barCode": CargoPlaceData.bar_code(),
                    "type": "free",
                    "sealNumber": "Пломба 4",
                    "wmsNumber": "Номер ВМС 4",
                    "category": 1,
                    "quantity": 40,
                    "requiredSentAt": CargoPlaceData.time_iso()[1],
                    "requiredDeliveredAt": CargoPlaceData.time_iso()[2],
                    "length": 1000,
                    "width": 1000,
                    "height": 1000,
                    "volume": 4500000,
                    "weight": 4500,
                    "reverseCargoType": None,
                    "reverseCargoReason": None,
                    "comment": None,
                    "invoiceNumber": "Накладная_замена4",
                    "invoiceDate": CargoPlaceData.time_iso()[0],
                    "innShipper": "5009112893",
                    "kppShipper": "500901001",
                    "innConsignee": "9705207762",
                    "kppConsignee": "770501001",
                    "cost": 40000,
                    "totalCost": 42000,
                    "departureAddressExternalId": None,
                    "departureAddress": departure_address,
                    "deliveryAddress": delivery_address,
                    "title": CargoPlaceData.name_cargo_place(),
                    "status": "new",
                    "statusAddressExternalId": None,
                    "externalId": None,
                    "isPlanned": True
                },
                {
                    "parentId": None,
                    "barCode": CargoPlaceData.bar_code(),
                    "type": "free",
                    "sealNumber": "Пломба 5",
                    "wmsNumber": "Номер ВМС 5",
                    "category": 1,
                    "quantity": 50,
                    "requiredSentAt": CargoPlaceData.time_iso()[1],
                    "requiredDeliveredAt": CargoPlaceData.time_iso()[2],
                    "length": 1000,
                    "width": 1000,
                    "height": 1000,
                    "volume": 5500000,
                    "weight": 5500,
                    "reverseCargoType": None,
                    "reverseCargoReason": None,
                    "comment": None,
                    "invoiceNumber": "Накладная_замена5",
                    "invoiceDate": CargoPlaceData.time_iso()[0],
                    "innShipper": "5009112893",
                    "kppShipper": "500901001",
                    "innConsignee": "9705207762",
                    "kppConsignee": "770501001",
                    "cost": 50000,
                    "totalCost": 52000,
                    "departureAddressExternalId": None,
                    "departureAddress": departure_address,
                    "deliveryAddress": delivery_address,
                    "title": CargoPlaceData.name_cargo_place(),
                    "status": "new",
                    "statusAddressExternalId": None,
                    "externalId": None,
                    "isPlanned": True
                }
            ]
        }

    @staticmethod
    def point_update(address_index: int):
        address_data = [
            {
                "id": 25515,
                "city_name": "Тольятти",
                "title": "первый адрес",
                "addressString": "Россия, Самарская обл, г Тольятти, б-р Ленина, д 12",
                "latitude": 53.50429942151597,
                "longitude": 49.418696761937994,
                "timezone": "Europe/Samara"
            },
            {
                "id": 25516,
                "city_name": "Уфа",
                "title": "второй адрес",
                "addressString": "Россия, г Уфа, ул Менделеева, д 1",
                "latitude": 54.71121298272444,
                "longitude": 55.971420813437916,
                "timezone": "Asia/Yekaterinburg"
            },
            {
                "id": 25517,
                "city_name": "Муром",
                "title": "третий адрес",
                "addressString": "Россия, Владимирская обл, г Муром, ул Мечникова, д 32",
                "latitude": 55.57179931529334,
                "longitude": 42.046804574743305,
                "timezone": "Europe/Moscow"
            },
            {
                "id": 25518,
                "city_name": "Мурманск",
                "title": "четвёртый адрес",
                "addressString": "Россия, г Мурманск, ул Академика Книповича, д 21",
                "latitude": 68.95952219390115,
                "longitude": 33.07934481833869,
                "timezone": "Europe/Moscow"
            }
        ]

        # берём нужный адрес по индексу
        addr = address_data[address_index]

        return {
            "addressString": addr["addressString"],
            "title": addr["title"],
            "timezone": addr["timezone"],
            "status": True,
            "latitude": addr["latitude"],
            "longitude": addr["longitude"],
            "cityName": addr["city_name"],
            "addressType": 1,
            "loadingType": 1,
            "liftingCapacityMax": None,
            "maxHeightFromGroundInCm": 0,
            "comment": None,
            "pointOwnerInn": "",
            "vicinityRadius": 2000,
            "pointOwnerKpp": "",
            "externalId": None,
            "pointArrivalDuration": 900,
            "pointDepartureDuration": 900,
            "necessaryPass": False,
            "statusFlowType": "fullFlow",
            "cart": 0,
            "isFavorite": 0,
            "elevator": 0,
            "id": addr["id"]
            }
        #     "data": [
        #         {
        #             "contacts": [
        #                 {
        #                     "contact": None,
        #                     "email": None,
        #                     "extraPhone": None,
        #                     "extraSecondPhone": None,
        #                     "phone": None,
        #                     "secondPhone": None
        #                 }
        #             ],
        #             "addressString": addr["addressString"],
        #             "title": addr["title"],
        #             "timezone": addr["timezone"],
        #             "status": True,
        #             "latitude": addr["latitude"],
        #             "longitude": addr["longitude"],
        #             "cityName": addr["city_name"],
        #             "addressType": 1,
        #             "loadingType": 1,
        #             "liftingCapacityMax": None,
        #             "maxHeightFromGroundInCm": 0,
        #             "comment": None,
        #             "pointOwnerInn": "",
        #             "vicinityRadius": 2000,
        #             "pointOwnerKpp": "",
        #             "externalId": None,
        #             "pointArrivalDuration": 900,
        #             "pointDepartureDuration": 900,
        #             "necessaryPass": False,
        #             "statusFlowType": "fullFlow",
        #             "cart": 0,
        #             "isFavorite": 0,
        #             "elevator": 0,
        #             "id": addr["id"]
        #         }
        #     ]
        # }

    # старые и новые адреса для 4 точек
    address_pairs = [
        {
            "old": "Гая",
            "new": "Ленина"
        },
        {
            "old": "Цюрупы",
            "new": "Менделеева"
        },
        {
            "old": "Свердлова",
            "new": "Мечникова"
        },
        {
            "old": "Плато",
            "new": "Книповича"
        }
    ]

    @staticmethod
    def cargo_place_list_feature(address_index: int, use_new: bool = False):

        today = date.today().strftime("%Y-%m-%d")

        addr = CargoPlacePayloadBuilder.address_pairs[address_index]
        delivery_addr = addr["new"] if use_new else addr["old"]

        return {
            "page": 1,
            "itemsPerPage": 1000,
            "creationDateFrom": today,
            "creationDateTo": today,
            "deliveryAddress": delivery_addr
        }

    # полные данные адресов (при вводе полного адреса не работает фильтр адрес доставки)
    address_name = [
        {
            "old": "Россия, Самарская обл, г Тольятти, б-р Гая, д 5",
            "new": "Россия, Самарская обл, г Тольятти, б-р Ленина, д 12"
        },
        {
            "old": "Россия, г Уфа, ул Цюрупы, д 13",
            "new": "Россия, г Уфа, ул Менделеева, д 1"
        },
        {
            "old": "Россия, Владимирская обл, г Муром, ул Свердлова, д 13",
            "new": "Россия, Владимирская обл, г Муром, ул Мечникова, д 32"
        },
        {
            "old": "Россия, г Мурманск, ул Новое Плато, д 10",
            "new": "Россия, г Мурманск, ул Академика Книповича, д 21"
        }
    ]

