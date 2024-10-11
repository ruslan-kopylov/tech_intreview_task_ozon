import requests
from requests.models import Response

from utils import check_response

DOGS_BASE_URL = 'https://dog.ceo/api/breed'


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
