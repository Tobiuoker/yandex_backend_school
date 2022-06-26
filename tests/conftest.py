import json
from flask_testing import TestCase

from project import create_app

import urllib

app = create_app("project.config.TestingConfig")

from project import db

init_data = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Товары",
                "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "parentId": None
            }
        ],
        "updateDate": "2022-02-01T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Телевизоры",
                "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
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
                "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 49999
            }
        ],
        "updateDate": "2022-02-03T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Goldstar 65\" LED UHD LOL Very Smart",
                "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 69999
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
]

class BaseTestCase(TestCase):
    def create_app(self):
        return app

    def initialize(self):
        for batch in init_data:
            self.request('/imports', 'POST', batch) 
            

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.initialize()
        
        db.session.commit() 


    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def request(self, path, method="GET", data=None, json_response=False):
        try:
            params = {
                "url": f"http://127.0.0.1/{path}",
                "method": method,
                "headers": {},
            }

            if data:
                params["data"] = json.dumps(
                    data, ensure_ascii=False).encode("utf-8")
                params["headers"]["Content-Length"] = len(params["data"])
                params["headers"]["Content-Type"] = "application/json"

            req = urllib.request.Request(**params)

            with urllib.request.urlopen(req) as res:
                res_data = res.read().decode("utf-8")
                if json_response:
                    res_data = json.loads(res_data)
                return (res.getcode(), res_data)
        except urllib.error.HTTPError as e:
            return (e.getcode(), e.read().decode("utf-8"))