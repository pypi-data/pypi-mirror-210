from typing import Any
import requests

def post(a: Any, url: str) -> Any:
    response = requests.post(url, data=a)
    return response.content
def get(a: str, url: str) -> str:
    response = requests.get(url, params={'a': a})
    return response.text

