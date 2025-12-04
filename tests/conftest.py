import logging
import pytest
import allure
from pathlib import Path

from api_client.client import JSONPlaceholderClient
from config.config import api_config, test_config


def setup_logging():
    log_dir = Path(test_config.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, test_config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


setup_logging()


@pytest.fixture(scope="session")
def api_client():
    client = JSONPlaceholderClient(
        base_url=api_config.BASE_URL,
        timeout=api_config.TIMEOUT
    )

    logging.info(f"API Client created: {api_config.BASE_URL}")
    yield client
    client.close()
    logging.info("API Client closed")


@pytest.fixture(scope="function")
def logger():
    return logging.getLogger("test")


@pytest.fixture(autouse=True)
def allure_environment(request):
    test_name = request.node.name
    allure.dynamic.parameter("test_name", test_name)
    allure.dynamic.parameter("base_url", api_config.BASE_URL)


@pytest.fixture
def test_post_data():
    return {
        "title": "Test Post from Pytest",
        "body": "This is a test post created during automated testing",
        "userId": 1
    }


@pytest.fixture
def test_user_id():
    return 1


@pytest.fixture
def test_post_id():
    return 1


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        if hasattr(item, 'funcargs'):
            for key, value in item.funcargs.items():
                if key != "request":
                    allure.attach(
                        str(value),
                        name=f"Fixture: {key}",
                        attachment_type=allure.attachment_type.TEXT
                    )


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: smoke tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "positive: positive scenarios")
    config.addinivalue_line("markers", "negative: negative scenarios")
