from lib.config import config


def pytest_configure():
    config._config["TEST_DB"] = True


def pytest_unconfigure():
    config._config["TEST_DB"] = False
