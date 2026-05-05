import os
import requests


API_BASE = os.getenv("DASHBOARD_API_BASE", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = 15
UPLOAD_TIMEOUT = 120


class ApiClientError(Exception):
    pass


def _build_url(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{API_BASE}{path}"


def _handle_response(response: requests.Response):
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        try:
            payload = response.json()
            detail = payload.get("detail") or str(payload)
        except Exception:
            detail = response.text or str(exc)
        raise ApiClientError(f"API error {response.status_code}: {detail}") from exc
    except ValueError as exc:
        raise ApiClientError("API response is not valid JSON") from exc


def get_json(path: str, params: dict | None = None):
    try:
        response = requests.get(
            _build_url(path),
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        raise ApiClientError(f"Failed GET {path}: {exc}") from exc


def post_json(path: str, payload: dict | None = None):
    try:
        response = requests.post(
            _build_url(path),
            json=payload or {},
            timeout=DEFAULT_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        raise ApiClientError(f"Failed POST {path}: {exc}") from exc


def put_json(path: str, payload: dict | None = None):
    try:
        response = requests.put(
            _build_url(path),
            json=payload or {},
            timeout=DEFAULT_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        raise ApiClientError(f"Failed PUT {path}: {exc}") from exc


def delete_json(path: str):
    try:
        response = requests.delete(
            _build_url(path),
            timeout=DEFAULT_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        raise ApiClientError(f"Failed DELETE {path}: {exc}") from exc


def post_files(path: str, files):
    """
    files example:
    [
        ("files", ("image1.jpg", file_bytes, "image/jpeg")),
        ("files", ("image2.png", file_bytes, "image/png")),
    ]
    """
    try:
        response = requests.post(
            _build_url(path),
            files=files,
            timeout=UPLOAD_TIMEOUT,
        )
        return _handle_response(response)
    except requests.RequestException as exc:
        raise ApiClientError(f"Failed FILE UPLOAD POST {path}: {exc}") from exc
