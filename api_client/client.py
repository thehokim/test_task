import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _log_request(self, method: str, url: str, **kwargs):
        self.logger.info(f"{method} {url}")
        if 'json' in kwargs:
            self.logger.debug(f"Payload: {kwargs['json']}")

    def _log_response(self, response: requests.Response):
        self.logger.info(f"{response.status_code} ({response.elapsed.total_seconds():.2f}s)")
        try:
            self.logger.debug(response.json())
        except ValueError:
            self.logger.debug(response.text)

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self._log_request("GET", url, **kwargs)
        response = self.session.get(url, timeout=self.timeout, **kwargs)
        self._log_response(response)
        return response

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self._log_request("POST", url, json=json, **kwargs)
        response = self.session.post(url, json=json, timeout=self.timeout, **kwargs)
        self._log_response(response)
        return response

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self._log_request("PUT", url, json=json, **kwargs)
        response = self.session.put(url, json=json, timeout=self.timeout, **kwargs)
        self._log_response(response)
        return response

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self._log_request("DELETE", url, **kwargs)
        response = self.session.delete(url, timeout=self.timeout, **kwargs)
        self._log_response(response)
        return response

    def close(self):
        self.session.close()


class JSONPlaceholderClient(APIClient):
    def get_posts(self, user_id: Optional[int] = None) -> requests.Response:
        params = {"userId": user_id} if user_id else None
        return self.get("posts", params=params)

    def get_post(self, post_id: int) -> requests.Response:
        return self.get(f"posts/{post_id}")

    def create_post(self, title: str, body: str, user_id: int) -> requests.Response:
        data = {"title": title, "body": body, "userId": user_id}
        return self.post("posts", json=data)

    def update_post(self, post_id: int, title: str, body: str, user_id: int) -> requests.Response:
        data = {"id": post_id, "title": title, "body": body, "userId": user_id}
        return self.put(f"posts/{post_id}", json=data)

    def delete_post(self, post_id: int) -> requests.Response:
        return self.delete(f"posts/{post_id}")

    def get_post_comments(self, post_id: int) -> requests.Response:
        return self.get(f"posts/{post_id}/comments")

    def get_users(self) -> requests.Response:
        return self.get("users")

    def get_user(self, user_id: int) -> requests.Response:
        return self.get(f"users/{user_id}")

    def get_comments(self, post_id: Optional[int] = None) -> requests.Response:
        params = {"postId": post_id} if post_id else None
        return self.get("comments", params=params)
