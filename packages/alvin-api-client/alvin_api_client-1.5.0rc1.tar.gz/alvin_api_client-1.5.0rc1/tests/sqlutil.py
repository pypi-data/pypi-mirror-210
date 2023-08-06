from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

user = getenv("DATABASE_USER", "alvin_adm")
password = getenv("DATABASE_PASSWORD", "alvin_pass")
server = getenv("DATABASE_HOST", "127.0.0.1:5432")
db = getenv("DATABASE_NAME", "alvin_demo")


db_engine: Engine = create_engine(
    f"postgresql://{user}:{password}@{server}/{db}",
).execution_options(schema_translate_map={None: "monda_data"})