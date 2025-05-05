from starlette import status


class TestCreateGraph:
    @staticmethod
    def get_url() -> str:
        return "/api/graph"

    def test_base_scenario(self, client):
        data = {
            "nodes": [{"name": "A"}, {"name": "B"}],
            "edges": [{"source": "A", "target": "B"}]
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"id": 1}

    def test_validation_error_node_name_duplicate(self, client):
        data = {
            "nodes": [{"name": "A"}, {"name": "A"}],
            "edges": []
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "msg" in response.json()["detail"][0]

    def test_validation_error_node_name(self, client):
        data = {
            "nodes": [{"name": "Ф"}, {"name": "B"}],  # не латинская буква Ф
            "edges": [{"source": "Ф", "target": "B"}]
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_node_name_longer_255(self, client):
        long_node_name = "A"*256
        data = {
            "nodes": [{"name": long_node_name}, {"name": "B"}],  # слишком длинное имя ноды
            "edges": [{"source": long_node_name, "target": "B"}]
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_node_in_edge(self, client):
        data = {
            "nodes": [{"name": "A"}, {"name": "B"}],
            "edges": [{"source": "C", "target": "B"}]  # нода C которой нет в nodes
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_sycle_in_graph(self, client):
        data = {
            "nodes": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
            "edges": [{"source": "A", "target": "B"}, {"source": "B", "target": "C"}, {"source": "C", "target": "A"}] # цикл  A -> B -> C -> A
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_empty_graph(self, client):
        data = {
            "nodes": [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_missing_edges(self, client):
        data = {
            "nodes": [],
        }
        response = client.post(url=self.get_url(), json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
