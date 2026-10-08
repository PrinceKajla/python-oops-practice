import os
from pathlib import Path

from dotenv import load_dotenv


class DatabaseConfigurationError(ValueError):
    pass


def get_database_config():
    load_dotenv(Path(__file__).with_name(".env"))
    required = {
        "host": "DB_HOST",
        "port": "DB_PORT",
        "dbname": "DB_NAME",
        "user": "DB_USER",
        "password": "DB_PASSWORD",
    }
    values = {key: os.getenv(env_name) for key, env_name in required.items()}
    missing = [required[key] for key, value in values.items() if not value]
    if missing:
        raise DatabaseConfigurationError(
            "Missing database configuration: " + ", ".join(missing)
        )
    try:
        values["port"] = int(values["port"])
    except (TypeError, ValueError):
        raise DatabaseConfigurationError("DB_PORT must be an integer.") from None
    return values
