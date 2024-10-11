import http
import os
import random

import pytest
import requests
from requests.models import Response


DOGS_BASE_URL = 'https://dog.ceo/api/breed'


def check_response(response: Response):
    if response.status_code != http.HTTPStatus.OK:
        raise ConnectionError(f'Status code {response.status_code}')


class YaUploader:
    base_url = 'https://cloud-api.yandex.net/v1/disk/resources{}'

    def __init__(self, token: str):
        self.token = token

    def create_folder(self, path: str) -> None:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}',
        }
        response = requests.put(self.base_url.format(f'?path={path}'), headers=headers)
        check_response(response)

    def upload_photos_to_yd(self, path: str, url_file: str, name: str) -> None:
        url = self.base_url.format('/upload')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}',
        }
        params = {'path': f'/{path}/{name}', 'url': url_file, 'overwrite': 'true'}
        response = requests.post(url, headers=headers, params=params)
        check_response(response)

    def get_photos(self, folder: str) -> Response:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        response = requests.get(self.base_url.format(f'?path=/{folder}'), headers=headers)
        check_response(response)
        return response


def get_sub_breeds(breed: str) -> list:
    response = requests.get(f'{DOGS_BASE_URL}/{breed}/list')
    check_response(response)
    return response.json().get('message', [])


def get_urls(breed: str, sub_breeds: list) -> list:
    url_images = []
    request_urls = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            request_urls.append(f'{DOGS_BASE_URL}/{breed}/{sub_breed}/images/random')
    else:
        request_urls.append(f'{DOGS_BASE_URL}/{breed}/images/random')
    for url in request_urls:
        response = requests.get(url)
        check_response(response)
        url_images.append(response.json().get('message'))
    return url_images


def upload_photos(breed: str, folder: str, client: YaUploader):
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    client.create_folder(folder)
    for url in urls:
        part_name = url.split('/')
        name = '_'.join([part_name[-2], part_name[-1]])
        client.upload_photos_to_yd(path=folder, url_file=url, name=name)


@pytest.fixture
def yandex_client():
    return YaUploader(token=os.getenv('TOKEN', 'AgAAAAAJtest_tokenxkUEdew'))


@pytest.fixture
def folder():
    return 'test_folder'


@pytest.fixture(scope='session', params=['doberman', random.choice(['bulldog', 'collie'])])
def breed(request):
    yield request.param


@pytest.fixture
def prepare_photos(breed, folder, yandex_client):
    yield upload_photos(breed=breed, folder=folder, client=yandex_client)


@pytest.fixture
def get_photos(prepare_photos, yandex_client, folder):
    return yandex_client.get_photos(folder=folder)


@pytest.fixture
def sub_breeds(breed):
    return get_sub_breeds(breed)


def test_upload_dog(get_photos, breed, sub_breeds):

    assert get_photos.status_code == http.HTTPStatus.OK

    assert get_photos.json()['type'] == 'dir'
    assert get_photos.json()['name'] == 'test_folder'

    response_items = get_photos.json()['_embedded']['items']
    response_len = len(sub_breeds) if sub_breeds else 1

    assert len(response_items) == response_len
    for item in response_items:
        assert item['type'] == 'file'
        assert item['name'].startswith(breed)

