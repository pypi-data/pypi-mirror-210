import configparser
from pathlib import Path

from alvin_api_client import ApiClient, Configuration
from alvin_api_client.api.default_api import DefaultApi
from sqlalchemy import text

from tests.sqlutil import db_engine

config = configparser.ConfigParser()
home = Path.home()
config.read(f"{home}/.alvin/alvin.cfg")
api_token = config.get("ALVIN", "alvin_api_token")

client = ApiClient(
    Configuration(host="http://localhost:8000"),
    header_name="X-API-KEY",
    header_value=api_token,
)

api = DefaultApi(client)

# TODO: isolate above code

# TODO: figure out why the API client is checking for non required return fields here
response = api.get_user_info_api_v1_me_get(_check_return_type=False)
assert response["org_id"] == "alv"

f = open("tests/integration/add_entity.sql", "r")
add_entity = f.read()
f.close()
f = open("tests/integration/delete_entity.sql", "r")
delete_entity = f.read()
f.close()

with db_engine.connect() as c:
    c.execute(text(add_entity))
    try:
        # Test here
        from alvin_api_client.model.data_entity_type import DataEntityType

        res = api.get_entity_api_v1_entity_get(
            platform_id="bigquery",
            entity_id="alvinai.analytics_demo_v1_safe.employees_us",
            entity_type=DataEntityType("TABLE"),
            _check_return_type=False,
            _return_http_data_only=True,
        )
        assert res["id"] == "dvdrental.public.film_actor__test"
        assert res["entity_type"] == "TABLE"
        assert res["name"] == "film_actor"
    finally:
        c.execute(text(delete_entity))

# TODO: move other tests elsewhere