import http


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

