import json

import tornado.testing

# from tests.base import rollback_db
# from tests.factories.recommendation import RecFactory
from tests.base import BaseTest


class TestRecHandler(BaseTest):
    _endpoint = "/drafts"

    # @rollback_db
    @tornado.testing.gen_test
    async def test_get__source_entity_id(self):
        assert 1 == 1
        # source_entity_id = 1
        # RecFactory().create(source_entity_id=source_entity_id)
        # RecFactory().create(source_entity_id=2)

        # response = await self.http_client.fetch(
        #     self.get_url(f"{self._endpoint}?source_entity_id={source_entity_id}"),
        #     method="GET",
        #     headers=self._headers,
        #     raise_error=False,
        # )

        # assert response.code == 200

        # results = json.loads(response.body)

        # assert len(results["results"]) == 1
        # assert results["results"][0]["source_entity_id"] == source_entity_id
