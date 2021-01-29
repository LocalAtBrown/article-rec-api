from lib.config import config
from db.mappings.model import Model
from db.mappings.article import Article
from db.mappings.recommendation import Rec
from db.mappings import database


MAPPINGS = (Model, Article, Rec)


def recreate_tables(db):
    db.drop_tables(MAPPINGS)
    db.create_tables(MAPPINGS)


def pytest_configure():
    config._config["TEST_DB"] = True
    recreate_tables(database)


def pytest_unconfigure():
    config._config["TEST_DB"] = False
