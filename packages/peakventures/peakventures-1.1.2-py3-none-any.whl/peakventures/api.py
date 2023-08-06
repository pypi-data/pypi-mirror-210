import functools

import requests
from tenacity import retry, wait_exponential, stop_after_attempt

from peakventures.credentials import get_credentials_json, API_CREDENTIALS_NAME

BASE_URL_V1 = "https://api.peakventures.co"
BASE_URL_V2 = "https://live.adtechapi.xyz"


@functools.lru_cache(maxsize=1)
def _get_session() -> requests.Session:
    credentials = get_credentials_json(API_CREDENTIALS_NAME)

    session = requests.Session()

    auth_response = session.post("https://peakventures.us.auth0.com/oauth/token", credentials)
    auth_response.raise_for_status()

    auth_response_json = auth_response.json()

    session.headers = {
        "Authorization": f"{auth_response_json['token_type']} {auth_response_json['access_token']}"
    }

    return session


@retry(wait=wait_exponential(1), stop=stop_after_attempt(3))
def get_topic(topic: str) -> dict:
    """Get topic by id."""
    session = _get_session()

    response = session.get(f"{BASE_URL_V2}/topics/{topic}")
    response.raise_for_status()

    return response.json()


@retry(wait=wait_exponential(1), stop=stop_after_attempt(3))
def update_sellside_keywords_weights(topic: str, weights: dict) -> None:
    """Update sellside weights."""
    session = _get_session()

    v1_response = session.put(f"{BASE_URL_V1}/topics/{topic}/keywords", json={
        "type": "sellside",
        "weights": weights
    })

    v1_response.raise_for_status()

    v2_response = session.put(f"{BASE_URL_V2}/topics/{topic}/keywords", json={
        "type": "sellside",
        "weights": weights
    })

    v2_response.raise_for_status()


@retry(wait=wait_exponential(1), stop=stop_after_attempt(3))
def get_topic_afd_domains(topic: str) -> list:
    """Get topic AFD domains."""
    session = _get_session()

    response = session.get(f"{BASE_URL_V2}/topics/{topic}")
    response.raise_for_status()

    topic = response.json()

    return topic["properties"]["afdMappings"]


__all__ = [
    "get_topic",
    "get_topic_afd_domains",
    "update_sellside_keywords_weights"
]
