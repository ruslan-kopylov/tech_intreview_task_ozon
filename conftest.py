import os
import random

import pytest

from uploader import YaUploader, upload_photos, get_sub_breeds


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

