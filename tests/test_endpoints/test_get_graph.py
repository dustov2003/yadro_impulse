from starlette import status


class TestGetGraph:
    @staticmethod
    def get_url(graph_id: int) -> str:
        return f"/api/graph/{graph_id}"

    def test_base_scenario(self, client, dag_sample):
        response = client.get(url=self.get_url(dag_sample.dag_id))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'id': dag_sample.dag_id,
                                   'nodes': [{'name': 'A'}, {'name': 'B'}, {'name': 'C'}, {'name': 'D'}, {'name': 'E'}],
                                   'edges': [{'source': 'A', 'target': 'B'}, {'source': 'A', 'target': 'C'},
                                             {'source': 'B', 'target': 'C'}, {'source': 'C', 'target': 'D'},
                                             {'source': 'D', 'target': 'E'}]}

    def test_graph_not_found(self, client, dag_sample):
        response = client.get(url=self.get_url(dag_sample.dag_id + 99))  # тот dag_id которого точно нет
        assert response.status_code == status.HTTP_404_NOT_FOUND
