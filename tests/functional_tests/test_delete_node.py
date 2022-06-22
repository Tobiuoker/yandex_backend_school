from tests.conftest import BaseTestCase

class DeleteNodeTest(BaseTestCase):
    def test_delete_node(self):        
        status, response = self.request(f'/nodes/069cb8d7-bbdd-47d3-ad8f-82ef4c269df1', json_response=True)

        # Сохраняем детей, чтобы потом проверить, что они тоже удалятся
        node_children = [i["id"] for i in response.get("children")]
        
        assert status == 200

        status, _ = self.request(f'/delete/069cb8d7-bbdd-47d3-ad8f-82ef4c269df1', 'DELETE')

        assert status == 200

        for i in node_children:
            status, _ = self.request(f'/nodes/{i}', json_response=True)

            # Проверяем, что после удаления основного объекта, удалятся также и дети
            assert status == 404