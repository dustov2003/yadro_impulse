from starlette import status


class TestGetGraphAdjacencyList:
    @staticmethod
    def get_url(graph_id: int) -> str:
        return f"/api/graph/{graph_id}/adjacency_list"

    def test_base_scenario(self, client, dag_sample):
        response = client.get(url=self.get_url(dag_sample.dag_id))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "adjacency_list": {
                "A": ["B", "C"],
                "B": ["C"],
                "C": ["D"],
                "D": ["E"],
                "E": [],
            }
        }

    def test_graph_not_found(self, client, dag_sample):
        response = client.get(
            url=self.get_url(dag_sample.dag_id + 99)
        )  # тот dag_id которого точно нет
        assert response.status_code == status.HTTP_404_NOT_FOUND
