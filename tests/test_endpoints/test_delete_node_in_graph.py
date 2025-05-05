from starlette import status


class TestDeleteNodeInGraph:
    @staticmethod
    def get_url(graph_id: int, node_name: str) -> str:
        return f"/api/graph/{graph_id}/node/{node_name}"

    @staticmethod
    def get_url_get_graph(graph_id: int) -> str:
        return f"/api/graph/{graph_id}"


    def test_base_scenario(self, client, dag_sample):
        response = client.delete(url=self.get_url(dag_sample.dag_id,"C"))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response = client.get(url=self.get_url_get_graph(dag_sample.dag_id))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": dag_sample.dag_id,
            "nodes": [
                {
                    "name": "A"
                },
                {
                    "name": "B"
                },
                {
                    "name": "D"
                },
                {
                    "name": "E"
                }
            ],
            "edges": [
                {
                    "source": "A",
                    "target": "B"
                },
                {
                    "source": "D",
                    "target": "E"
                }
            ]
        }


    def test_graph_not_found(self, client, dag_sample):
        response = client.delete(url=self.get_url(dag_sample.dag_id + 99,"A"))  # тот dag_id которого точно нет
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_node_not_found_in_graph(self, client, dag_sample):
        response = client.delete(url=self.get_url(dag_sample.dag_id,"NONEXISTENNODE"))  # тот dag_id которого точно нет
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_all_nodes(self, client, dag_sample):
        nodes_name=['A','B','C','D','E']
        for node in nodes_name:
            response = client.delete(url=self.get_url(dag_sample.dag_id, node))
            assert response.status_code == status.HTTP_204_NO_CONTENT
        response = client.get(url=self.get_url_get_graph(dag_sample.dag_id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
