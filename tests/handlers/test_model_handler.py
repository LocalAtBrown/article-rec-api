import json

import tornado.testing

from tests.factories.model import ModelFactory
from tests.base import BaseTest
from db.mappings.model import Type, Status


class TestModelHandler(BaseTest):
    _endpoint = "/models"

    @tornado.testing.gen_test
    async def test_get__status__filter(self):
        current_mdl = ModelFactory.create(status=Status.CURRENT.value)
        pending_mdl = ModelFactory.create(status=Status.PENDING.value)

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?status={Status.CURRENT.value}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["status"] == Status.CURRENT.value

    @tornado.testing.gen_test
    async def test_get__type__filter(self):
        article_mdl = ModelFactory.create(type=Type.ARTICLE.value)
        user_mdl = ModelFactory.create(type=Type.USER.value)

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?type={Type.ARTICLE.value}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["type"] == Type.ARTICLE.value
