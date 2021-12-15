import json

import tornado.testing

from tests.factories.model import ModelFactory
from tests.factories.article import ArticleFactory
from tests.factories.recommendation import RecFactory
from tests.base import BaseTest
from db.mappings.model import Type, Status, Site, Model
from db.helpers import get_resource
from lib.config import config


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
        misc_model = ModelFactory.create(
            status=Status.CURRENT.value, site=Site.TEXAS_TRIBUNE.value
        )
        target_model = ModelFactory.create(
            status=Status.STALE.value, site=Site.TEXAS_TRIBUNE.value
        )

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

    @tornado.testing.gen_test
    async def test_patch__no_admin_token__throws_error(self):
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}/1/set_current"),
            method="PATCH",
            raise_error=False,
            allow_nonstandard_methods=True,
        )

        assert response.code == 401

    @tornado.testing.gen_test
    async def test_patch__wrong_admin_token__throws_error(self):
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}/1/set_current"),
            method="PATCH",
            raise_error=False,
            allow_nonstandard_methods=True,
            headers={"Authorization": "bad-auth"},
        )

        assert response.code == 403

    @tornado.testing.gen_test
    async def test_patch__missing_resource__throws_error(self):
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}/1/set_current"),
            method="PATCH",
            raise_error=False,
            allow_nonstandard_methods=True,
            headers={"Authorization": config.get("ADMIN_TOKEN")},
        )

        assert response.code == 404

    @tornado.testing.gen_test
    async def test_patch__good_admin_token__updates_resource(self):
        old_current = ModelFactory.create(
            status=Status.CURRENT.value, site=Site.TEXAS_TRIBUNE.value
        )
        new_current = ModelFactory.create(
            status=Status.STALE.value, site=Site.TEXAS_TRIBUNE.value
        )
        wrong_site = ModelFactory.create(
            status=Status.CURRENT.value, site=Site.WCP.value
        )

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}/{new_current['id']}/set_current"),
            method="PATCH",
            raise_error=False,
            allow_nonstandard_methods=True,
            headers={"Authorization": config.get("ADMIN_TOKEN")},
        )

        assert response.code == 200

        old_current = get_resource(Model, old_current["id"])
        new_current = get_resource(Model, new_current["id"])
        wrong_site = get_resource(Model, wrong_site["id"])
        assert old_current["status"] == Status.STALE.value
        assert new_current["status"] == Status.CURRENT.value
        assert wrong_site["status"] == Status.CURRENT.value
