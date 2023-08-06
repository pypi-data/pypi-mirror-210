import pytest


@pytest.mark.django_db
def test_redis_client_fixture(redis_client_fixture):
    redis_address, redis_port = redis_client_fixture

    assert redis_address == "127.0.0.1"
    assert redis_port == 6379


@pytest.mark.django_db
def test_translate_client_fixture(translate_client_fixture):
    client = translate_client_fixture

    assert client
    assert client.address == "http://localhost"
    assert client.port
    assert client.cache_address == "127.0.0.1"
