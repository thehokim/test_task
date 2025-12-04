import os
from dataclasses import dataclass


@dataclass
class APIConfig:
    BASE_URL: str = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")
    TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("API_MAX_RETRIES", "3"))
    RETRY_BACKOFF: int = int(os.getenv("API_RETRY_BACKOFF", "1"))


@dataclass
class TestConfig:
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    ALLURE_RESULTS_DIR: str = os.getenv("ALLURE_RESULTS_DIR", "allure-results")
    PARALLEL_ENABLED: bool = os.getenv("PARALLEL_ENABLED", "false").lower() == "true"
    PARALLEL_WORKERS: int = int(os.getenv("PARALLEL_WORKERS", "4"))


api_config = APIConfig()
test_config = TestConfig()
