import json

import tornado.testing

from tests.factories.recommendation import RecFactory
from tests.factories.model import ModelFactory
from tests.factories.article import ArticleFactory
from tests.base import BaseTest


class TestRecHandler(BaseTest):
    _endpoint = "/recs"

    @tornado.testing.gen_test
    async def test_get__source_entity_id(self):
        model = ModelFactory.create()
        article = ArticleFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        source_entity_id = "1"
        RecFactory().create(
            model_id=model["id"],
            recommended_article_id=article["id"],
            source_entity_id=source_entity_id,
        )

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?source_entity_id={source_entity_id}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["source_entity_id"] == source_entity_id

    @tornado.testing.gen_test
    async def test_get__model_id(self):
        article = ArticleFactory.create()
        first_mdl = ModelFactory.create()
        RecFactory.create(model_id=first_mdl["id"], recommended_article_id=article["id"])
        second_mdl = ModelFactory.create()
        RecFactory().create(model_id=second_mdl["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?model_id={first_mdl['id']}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["model"]["id"] == first_mdl["id"]
