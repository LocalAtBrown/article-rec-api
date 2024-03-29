import json

import tornado.testing

from db.mappings.model import Site, Status, Type
from tests.base import BaseTest
from tests.factories.article import ArticleFactory
from tests.factories.model import ModelFactory
from tests.factories.recommendation import RecFactory


class TestModelArticleHandler(BaseTest):
    _endpoint = "/models"

    @tornado.testing.gen_test
    async def test_get__missing_resource__throws_error(self):
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}/1/articles"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 404

    @tornado.testing.gen_test
    async def test_get(self):
        misc_model = ModelFactory.create(status=Status.CURRENT.value, site=Site.TEXAS_TRIBUNE.value)
        target_model = ModelFactory.create(status=Status.STALE.value, site=Site.TEXAS_TRIBUNE.value)

        misc_article = ArticleFactory.create(site=Site.TEXAS_TRIBUNE.value)
        target_article_1 = ArticleFactory.create(site=Site.TEXAS_TRIBUNE.value)
        target_article_2 = ArticleFactory.create(site=Site.TEXAS_TRIBUNE.value)

        recommended_article = ArticleFactory.create(site=Site.TEXAS_TRIBUNE.value)

        RecFactory.create(
            model_id=misc_model["id"],
            source_entity_id=misc_article["external_id"],
            recommended_article_id=recommended_article["id"],
        )
        RecFactory.create(
            model_id=misc_model["id"],
            source_entity_id=target_article_1["external_id"],
            recommended_article_id=recommended_article["id"],
        )

        RecFactory.create(
            model_id=target_model["id"],
            source_entity_id=target_article_1["external_id"],
            recommended_article_id=recommended_article["id"],
        )
        RecFactory.create(
            model_id=target_model["id"],
            source_entity_id=target_article_2["external_id"],
            recommended_article_id=recommended_article["id"],
        )

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}/{target_model['id']}/articles"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        articles = results["results"]
        assert len(articles) == 2

        article_ids = {a["id"] for a in articles}
        assert target_article_1["id"] in article_ids
        assert target_article_2["id"] in article_ids


class TestModelHandler(BaseTest):
    _endpoint = "/models"

    @tornado.testing.gen_test
    async def test_get__status__filter(self):
        ModelFactory.create(status=Status.CURRENT.value)
        ModelFactory.create(status=Status.PENDING.value)

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
        ModelFactory.create(type=Type.ARTICLE.value)
        ModelFactory.create(type=Type.USER.value)

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?type={Type.ARTICLE.value}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["type"] == Type.ARTICLE.value

    @tornado.testing.gen_test
    async def test_get__site__filter(self):
        ModelFactory.create(site="washington-city-paper")
        ModelFactory.create(site="texas-tribune")

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site=texas-tribune"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["site"] == "texas-tribune"
