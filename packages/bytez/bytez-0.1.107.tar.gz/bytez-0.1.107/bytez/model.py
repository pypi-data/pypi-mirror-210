from typing import Union, List
from dataclasses import dataclass
import requests
import os

@dataclass
class Model:
    # private, requires a mangled name
    def __inference(self, url: str, request_params: dict) -> bytes:
        files = {}
        data = {}

        for key, value in request_params.items():
            if value is None:
                continue

            if isinstance(value, list):
                # Convert list values to the appropriate format
                for item in value:
                    data.setdefault(key, []).append(str(item))
            elif hasattr(value, 'read') and callable(value.read):
                files[key] = value
            else:
                if not isinstance(value, str):
                    value = str(value)
                data[key] = value

        if os.getenv("TEST"):
            url = "http://localhost:8080"


        response = requests.post(url, files=files, data=data)

        if not response.ok:
            raise Exception(f'Request failed with {response.status_code}')

        return response.content