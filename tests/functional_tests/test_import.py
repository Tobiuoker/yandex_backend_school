from tests.conftest import BaseTestCase

class ImportTest(BaseTestCase):
    def test_import_success_code(self):
        """
            Тестируется правильность кода ответа
        """

        unit_id = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
        unit_date = "2021-02-02T12:00:00.000Z"
        data = {
                "items": [
                    {
                        "type": "CATEGORY",
                        "name": "Товары",
                        "id": unit_id,
                        "parentId": None,
                        "children": []
                    }
                ],
                "updateDate": f"{unit_date}"
            }

        status, _ = self.request('/imports', 'POST', data) 
        assert status == 200

    def test_import_success_update(self):
        """
            Тестируется обновление элемента (на примере правильности обновления даты)
        """

        unit_id = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
        unit_date = "2021-02-02T12:00:00.000Z"

        data = {
                "items": [
                    {
                        "type": "CATEGORY",
                        "name": "Товары",
                        "id": unit_id,
                        "parentId": None,
                        "children": []
                    }
                ],
                "updateDate": f"{unit_date}"
            }

        self.request('/imports', 'POST', data) 

        response = self.client.get(
            '/nodes/069cb8d7-bbdd-47d3-ad8f-82ef4c269df1',
        )

        status, response = self.request(f'/nodes/{unit_id}', json_response=True)

        assert status == 200

        assert unit_date == response["date"]

    def test_import_success_parent_update(self):
        """
            Тестируется обновление даты родительского элемента, в случае обновления даты дочернего
        """

        unit_id = "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2"
        parent_id = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"

        unit_date = "2021-02-02T12:00:00.000Z"

        data = {
                "items": [
                    {
                        "type": "CATEGORY",
                        "name": "Товары",
                        "id": unit_id,
                        "parentId": parent_id,
                        "children": []
                    }
                ],
                "updateDate": f"{unit_date}"
            }

        self.request('/imports', 'POST', data) 

        status, response = self.request(f'/nodes/{parent_id}', json_response=True)

        assert status == 200

        assert unit_date == response["date"]

    def test_import_empty_data(self):
        data = {}

        status, response = self.request('/imports', 'POST', data) 

        assert status == 400

        # assert response == "Невалидная схема документа или входные данные не верны."

    def test_import_duplicate_ids(self):
        data = {
            "items": [
                {
                    "type": "CATEGORY",
                    "name": "Телевизоры",
                    "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                },
                {
                    "type": "OFFER",
                    "name": "Samson 70\" LED UHD Smart",
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 32999
                },
                {
                    "type": "OFFER",
                    "name": "Phyllis 50\" LED UHD Smarter",
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 49999
                }
            ],
            "updateDate": "2023-02-03T12:00:00Z"
        }

        status, response = self.request('/imports', 'POST', data) 

        assert status == 400

        assert response == "В одном запросе не может быть двух элементов с одинаковым id"

    def test_import_parent_offer(self):
        unit_id = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
        unit_date = "2021-02-01T12:00:00Z"
        data = {
            "items": [
                    {
                    "type": "OFFER",
                    "name": "Samson 70\" LED UHD Smart",
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 32999,
                },
                {
                    "type": "OFFER",
                    "name": "Phyllis 50\" LED UHD Smarter",
                    "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                    "parentId": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "price": 49999
                }
            ],
            "updateDate": f"{unit_date}"
        }

        status, response = self.request('/imports', 'POST', data)

        assert status == 400

        assert response == "Родителем товара или категории может быть только категория"

    def test_import_empty_name(self):
        data = {
            "items": [
                {
                    "type": "OFFER",
                    "name": None,
                    "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "parentId": "",
                }
            ],
            "updateDate": "2021-02-01T12:00:00Z"
        }

        status, response = self.request('/imports', 'POST', data)

        assert status == 400

        assert response == "Название элемента не может быть null"

    def test_import_category_price(self):
        data = {
            "items": [
                {
                    "type": "CATEGORY",
                    "name": "Телевизоры",
                    "price": 123,
                    "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "parentId": "",
                }
            ],
            "updateDate": "2021-02-01T12:00:00Z"
        }

        status, response = self.request('/imports', 'POST', data)

        assert status == 400

        assert response == "У категорий поле price должно содержать null"

    
    def test_import_change_type(self):
        data = {
            "items": [
                {
                    "type": "CATEGORY",
                    "name": "Phyllis 50\" LED UHD Smarter",
                    "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                }
            ],
            "updateDate": "2022-02-03T12:00:00.000Z"
        }

        status, response = self.request('/imports', 'POST', data)

        assert status == 400

        assert response == "Изменение типа элемента с товара на категорию или с категории на товар не допускается"


    def test_import_change_parent_id(self):
        data = {
            "items": [
                {
                "type": "OFFER",
                "name": "Phyllis 50\" LED UHD Smarter",
                "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 49999
            }
            ],
            "updateDate": "2022-02-03T12:00:00.000Z"
        }

        _, response = self.request(f'/nodes/1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2', json_response=True)

        # Проверяем, что объект действительно являлся child'ом 1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2 

        assert "74b81fda-9cdc-4b63-8927-c978afed5cf4" in [i["id"] for i in response.get("children")]

        self.request('/imports', 'POST', data)

        _, response = self.request(f'/nodes/069cb8d7-bbdd-47d3-ad8f-82ef4c269df1', json_response=True)

        # Проверяем, что после смены parentId на 069cb8d7-bbdd-47d3-ad8f-82ef4c269df1, 
        # этот объект появится у 069cb8d7-bbdd-47d3-ad8f-82ef4c269df1 в массиве child'ов

        assert "74b81fda-9cdc-4b63-8927-c978afed5cf4" in [i["id"] for i in response.get("children")]

        _, response = self.request(f'/nodes/1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2', json_response=True)

        # Проверяем, что объект больше не является ребенком 1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2

        assert "74b81fda-9cdc-4b63-8927-c978afed5cf4" not in [i["id"] for i in response.get("children")]
