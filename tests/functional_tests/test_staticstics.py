from tests.conftest import BaseTestCase

EXPECTED_RESULT = [
  {
    "date": "2022-02-02T12:00:00.000Z", 
    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1", 
    "name": "Товары", 
    "parentId": None, 
    "price": 69999, 
    "type": "CATEGORY"
  }, 
  {
    "date": "2022-02-02T12:00:00.000Z", 
    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1", 
    "name": "Товары", 
    "parentId": None, 
    "price": 79999, 
    "type": "CATEGORY"
  }
]

class StatisticsTest(BaseTestCase):
    def test_statistics(self):
        startDate = "2022-02-01T00:00:00.000Z"
        endDate = "2022-02-03T00:00:00.000Z"
        id = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"

        status, response = self.request(f'/node/{id}/statistic?dateStart={startDate}&dateEnd={endDate}', json_response=True)

        assert status == 200

        assert [i for i in response if i not in EXPECTED_RESULT] == []