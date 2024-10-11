import http

from requests.models import Response


def check_response(response: Response):
    if response.status_code != http.HTTPStatus.OK:
        raise ConnectionError(f'Status code {response.status_code}')
