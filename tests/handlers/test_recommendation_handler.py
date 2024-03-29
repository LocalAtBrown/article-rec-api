import json

import tornado.testing

from db.mappings.model import Status, Type
from handlers.recommendation import TTL_CACHE
from lib.config import config
from tests.base import BaseTest
from tests.factories.article import ArticleFactory
from tests.factories.model import ModelFactory
from tests.factories.recommendation import RecFactory

MAX_PAGE_SIZE = config.get("MAX_PAGE_SIZE")


class TestRecHandler(BaseTest):
    _endpoint = "/recs"

    def setUp(self) -> None:
        TTL_CACHE.clear()
        super().setUp()

    @tornado.testing.gen_test
    async def test_get__size__limits_items(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        size = 2
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?size={size}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        assert len(results["results"]) == size

    @tornado.testing.gen_test
    async def test_get__size__default_items__size_less_than_res(self):
        article = ArticleFactory.create()
        model = ModelFactory.create(type=Type.POPULARITY.value, status=Status.CURRENT.value)
        recs = [
            RecFactory.create(model_id=model["id"], recommended_article_id=article["id"]),
            RecFactory.create(model_id=model["id"], recommended_article_id=article["id"]),
            RecFactory.create(model_id=model["id"], recommended_article_id=article["id"]),
        ]
        size = len(recs) - 1
        site = config.get("DEFAULT_SITE")
        request_type = Type.ARTICLE.value
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={site}&model_type={request_type}&size={size}"),
            method="GET",
            raise_error=False,
        )
        assert response.code == 200
        results = json.loads(response.body)
        assert len(results["results"]) == size

    @tornado.testing.gen_test
    async def test_get__size__default_items__size_greater_than_res(self):
        article = ArticleFactory.create()
        model = ModelFactory.create(type=Type.POPULARITY.value, status=Status.CURRENT.value)
        recs = [
            RecFactory.create(model_id=model["id"], recommended_article_id=article["id"]),
            RecFactory.create(model_id=model["id"], recommended_article_id=article["id"]),
            RecFactory.create(model_id=model["id"], recommended_article_id=article["id"]),
        ]
        size = len(recs) + 1
        site = config.get("DEFAULT_SITE")
        request_type = Type.ARTICLE.value
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={site}&model_type={request_type}&size={size}"),
            method="GET",
            raise_error=False,
        )
        assert response.code == 200
        results = json.loads(response.body)
        assert len(results["results"]) == len(recs)

    @tornado.testing.gen_test
    async def test_get__invalid_size__raises_error(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        invalid_size = MAX_PAGE_SIZE * 2
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?size={invalid_size}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 400

        results = json.loads(response.body)

        expected_msg = f"Invalid input for 'size' (int), must be below {MAX_PAGE_SIZE}: {invalid_size}"
        assert results["message"] == expected_msg

    @tornado.testing.gen_test
    async def test_get__site_filter_default(self):
        """
        If fetching recommendations for an article not in the DB,
        respond with site-filtered default recommendations
        """
        popularity_model = ModelFactory.create(type=Type.POPULARITY.value)

        article0 = ArticleFactory.create(site="site1")
        article1 = ArticleFactory.create(site="site1")
        article2 = ArticleFactory.create(site="site2")
        RecFactory.create(
            model_id=popularity_model["id"],
            recommended_article_id=article1["id"],
        )
        RecFactory.create(
            model_id=popularity_model["id"],
            recommended_article_id=article2["id"],
        )

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?source_entity_id={article0['id']}&site={'site1'}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["recommended_article"]["external_id"] == article1["external_id"]
        assert results["results"][0]["model"]["id"] == popularity_model["id"]

    @tornado.testing.gen_test
    async def test_get__site_filter(self):
        model = ModelFactory.create()
        article1 = ArticleFactory.create(site="site1")
        article2 = ArticleFactory.create(site="site2")
        RecFactory.create(model_id=model["id"], recommended_article_id=article1["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article2["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={'site1'}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["recommended_article"]["external_id"] == article1["external_id"]

    @tornado.testing.gen_test
    async def test_get__source_entity_id__filter(self):
        model = ModelFactory.create()
        article = ArticleFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        source_entity_id = "1"
        RecFactory.create(
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
    async def test_get__model_id__filter(self):
        article = ArticleFactory.create()
        first_mdl = ModelFactory.create()
        RecFactory.create(model_id=first_mdl["id"], recommended_article_id=article["id"])
        second_mdl = ModelFactory.create()
        RecFactory.create(model_id=second_mdl["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?model_id={first_mdl['id']}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["model"]["id"] == first_mdl["id"]

    @tornado.testing.gen_test
    async def test_get__model_id__overrides_model_type(self):
        article = ArticleFactory.create()
        user_mdl = ModelFactory.create(type=Type.USER.value, status=Status.PENDING.value)
        RecFactory.create(model_id=user_mdl["id"], recommended_article_id=article["id"])
        article_mdl = ModelFactory.create(type=Type.ARTICLE.value)
        RecFactory.create(model_id=article_mdl["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?model_id={user_mdl['id']}&model_type={article_mdl['type']}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["model"]["id"] == user_mdl["id"]

    @tornado.testing.gen_test
    async def test_get__model_type__pulls_current_model(self):
        article = ArticleFactory.create()
        pending_mdl = ModelFactory.create(type=Type.ARTICLE.value, status=Status.PENDING.value)
        RecFactory.create(model_id=pending_mdl["id"], recommended_article_id=article["id"])
        current_mdl = ModelFactory.create(type=Type.ARTICLE.value, status=Status.CURRENT.value)
        RecFactory.create(model_id=current_mdl["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?model_type={Type.ARTICLE.value}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)

        assert len(results["results"]) == 1
        assert results["results"][0]["model"]["id"] == current_mdl["id"]

    @tornado.testing.gen_test
    async def test_get__order_by__defaults_to_desc(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?sort_by=score"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        scores = [x["score"] for x in results["results"]]
        desc_scores = [x for x in reversed(sorted(scores))]
        self.assertListEqual(scores, desc_scores)

    @tornado.testing.gen_test
    async def test_get__order_by__overrides_default(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?sort_by=score&order_by=asc"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        scores = [x["score"] for x in results["results"]]
        asc_scores = [x for x in sorted(scores)]
        self.assertListEqual(scores, asc_scores)

    @tornado.testing.gen_test
    async def test_get__sort_by__invalid_ignored(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?sort_by=blah"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        assert len(results["results"]) == 4

    @tornado.testing.gen_test
    async def test_get__order_by__invalid_ignored(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?sort_by=score&order_by=blah"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        scores = [x["score"] for x in results["results"]]
        desc_scores = [x for x in reversed(sorted(scores))]
        self.assertListEqual(scores, desc_scores)

    @tornado.testing.gen_test
    async def test_get__exclude__filters_unwanted_ids(self):
        excluded_1 = ArticleFactory.create()
        excluded_2 = ArticleFactory.create()
        not_excluded = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=excluded_1["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=excluded_2["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=not_excluded["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=not_excluded["id"])

        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?exclude={excluded_1['external_id']},{excluded_2['external_id']}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        article_rec_ids = [x["recommended_article"]["id"] for x in results["results"]]
        self.assertListEqual(article_rec_ids, [not_excluded["id"]] * 2)

    @tornado.testing.gen_test
    async def test_get__exclude__works_with_model_type(self):
        not_excluded = ArticleFactory.create()
        user_mdl = ModelFactory.create(type=Type.USER.value, status=Status.CURRENT.value)
        RecFactory.create(model_id=user_mdl["id"], recommended_article_id=not_excluded["id"])

        excluded_1 = ArticleFactory.create()
        excluded_2 = ArticleFactory.create()
        article_mdl = ModelFactory.create(type=Type.ARTICLE.value, status=Status.CURRENT.value)
        RecFactory.create(model_id=article_mdl["id"], recommended_article_id=excluded_1["id"])
        RecFactory.create(model_id=article_mdl["id"], recommended_article_id=excluded_2["id"])
        RecFactory.create(model_id=article_mdl["id"], recommended_article_id=not_excluded["id"])

        response = await self.http_client.fetch(
            self.get_url(
                f"{self._endpoint}?exclude={excluded_1['external_id']},{excluded_2['external_id']}&model_type={Type.ARTICLE.value}"
            ),
            method="GET",
            raise_error=False,
        )

        assert response.code == 200

        results = json.loads(response.body)
        assert len(results["results"]) == 1
        assert results["results"][0]["recommended_article"]["id"] == not_excluded["id"]
        assert results["results"][0]["model"]["id"] == article_mdl["id"]

    @tornado.testing.gen_test
    async def test_get__invalid_exclude(self):
        invalid_id = "not_an_int"
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?exclude=1,{invalid_id}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 400

        results = json.loads(response.body)

        expected_msg = f"Invalid input for 'exclude' (List[int]): 1,{invalid_id}"
        assert results["message"] == expected_msg

    @tornado.testing.gen_test
    async def test_get__invalid_model_id(self):
        invalid_id = "not_an_int"
        response = await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?model_id={invalid_id}"),
            method="GET",
            raise_error=False,
        )

        assert response.code == 400

        results = json.loads(response.body)

        expected_msg = f"Invalid input for 'model_id' (int): {invalid_id}"
        assert results["message"] == expected_msg

    @tornado.testing.gen_test
    async def test_get__duplicate_requests(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        size = 2
        site = config.get("DEFAULT_SITE")
        await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={site}&size={size}"),
            method="GET",
            raise_error=False,
        )

        assert len(TTL_CACHE.keys()) == 1

        # duplicate request
        await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={site}&size={size}"),
            method="GET",
            raise_error=False,
        )

        assert len(TTL_CACHE.keys()) == 1

    @tornado.testing.gen_test
    async def test_get__different_requests(self):
        article = ArticleFactory.create()
        model = ModelFactory.create()
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])
        RecFactory.create(model_id=model["id"], recommended_article_id=article["id"])

        size = 2
        site = config.get("DEFAULT_SITE")
        await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={site}&size={size}"),
            method="GET",
            raise_error=False,
        )

        assert len(TTL_CACHE.keys()) == 1

        # different request
        await self.http_client.fetch(
            self.get_url(f"{self._endpoint}?site={site}&size={size + 1}"),
            method="GET",
            raise_error=False,
        )

        assert len(TTL_CACHE.keys()) == 2
