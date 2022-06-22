from tests.conftest import BaseTestCase

EXPECTED_RESULT = [
  {
    "children": None, 
    "date": "2022-02-02T12:00:00.000Z", 
    "id": "863e1a7a-1304-42ae-943b-179184c077e3", 
    "name": "jPhone 13", 
    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2", 
    "price": 79999, 
    "type": "OFFER"
  }, 
  {
    "children": None, 
    "date": "2022-02-02T12:00:00.000Z", 
    "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4", 
    "name": "Xomiа Readme 10", 
    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2", 
    "price": 59999, 
    "type": "OFFER"
  }, 
  {
    "children": [
      "863e1a7a-1304-42ae-943b-179184c077e3", 
      "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4"
    ], 
    "date": "2022-02-02T12:00:00.000Z", 
    "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2", 
    "name": "Смартфоны", 
    "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1", 
    "price": None, 
    "type": "CATEGORY"
  }
]

class SalesTest(BaseTestCase):
    def test_sales(self):
        date = "2022-02-03T12:00:00.000Z"

        status, response = self.request(f'/sales?date={date}', json_response=True)

        assert status == 200

        assert [i for i in response if i not in EXPECTED_RESULT] == []



