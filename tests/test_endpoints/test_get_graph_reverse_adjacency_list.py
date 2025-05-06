from starlette import status


class TestGetGraphReverseAdjacencyList:
    @staticmethod
    def get_url(graph_id: int) -> str:
        return f"/api/graph/{graph_id}/reverse_adjacency_list"

    def test_base_scenario(self, client, dag_sample):
        response = client.get(url=self.get_url(dag_sample.dag_id))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "adjacency_list": {
                "A": [],
                "B": ["A"],
                "C": ["A", "B"],
                "D": ["C"],
                "E": ["D"],
            }
        }

    def test_graph_not_found(self, client, dag_sample):
        response = client.get(
            url=self.get_url(dag_sample.dag_id + 99)
        )  # тот dag_id которого точно нет
        assert response.status_code == status.HTTP_404_NOT_FOUND
