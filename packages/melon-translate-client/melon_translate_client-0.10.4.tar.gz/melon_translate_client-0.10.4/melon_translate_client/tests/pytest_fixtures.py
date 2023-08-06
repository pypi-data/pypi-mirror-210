import pytest
from decouple import config
from redis import Redis


@pytest.fixture(scope="session")
def redis_client_fixture(request):
    """
    This fixture establishes a connection to Redis, and yields address and port of that connection
    """

    redis = Redis(
        host=config("REDIS_HOST", default="127.0.0.1", cast=str),
        port=config("REDIS_PORT", default=6379, cast=int),
        db=config("REDIS_DATABASE", default=0, cast=int),
        decode_responses=True,
        socket_timeout=30,
        socket_connect_timeout=30,
        max_connections=7500,
    )

    # Teardown code
    def teardown():
        # Clean up resources or perform any necessary cleanup
        redis.flushdb()
        redis.close()

    # Register the teardown function to be executed after the test session
    request.addfinalizer(teardown)

    connection_pool = redis.connection_pool

    # Access the address and port
    address = connection_pool.connection_kwargs["host"]
    port = connection_pool.connection_kwargs["port"]

    yield address, port


@pytest.fixture()
def translate_client_fixture(live_server, redis_client_fixture):
    """
    Fixture for creating melon-translate-client instance
    """
    from melon_translate_client import Client

    translate_url = live_server.url
    port = translate_url.split(":")[2]
    redis_address, redis_port = redis_client_fixture

    translate_client = Client(
        service_address=config("TRANSLATE_ADDRESS", default="http://localhost"),
        service_port=port,
        cache_address=redis_address,
        cache_port=redis_port,
    )

    yield translate_client
