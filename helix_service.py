# helix_service.py
import os
from typing import Any, Dict

import helix
from helix.client import Query
from helix.types import Payload

_db: helix.Client | None = None


def init_helix_client() -> helix.Client:
    """
    Initialize a HelixDB client.

    If HELIX_API_ENDPOINT is set, we connect to that.
    Otherwise, we assume a local Helix instance is running (default port 6969).
    """
    global _db
    if _db is not None:
        return _db

    api_endpoint = os.getenv("HELIX_API_ENDPOINT")
    if api_endpoint:
        # Remote/cloud Helix instance
        _db = helix.Client(api_endpoint=api_endpoint, verbose=True)
    else:
        # Local instance (you are responsible for starting helix separately)
        # `helix.Client(local=True)` connects to localhost:6969 by default.
        _db = helix.Client(local=True, verbose=True)

    return _db


# --- Example query class (you'll need a matching HelixQL query on the DB side) ---
# Docs pattern: define a HelixQL query (e.g. QUERY add_user) and mirror it here. :contentReference[oaicite:2]{index=2}

class AddUser(Query):
    def __init__(self, name: str, age: int):
        super().__init__()
        self.name = name
        self.age = age

    def query(self) -> Payload:
        # Must return a list of objects that match the HelixQL query parameters
        return [{"name": self.name, "age": self.age}]

    def response(self, response):
        # Just pass the raw response through; customize as needed
        return response


def helix_add_user(name: str, age: int) -> Any:
    db = init_helix_client()
    return db.query(AddUser(name, age))


# You can define more query classes + helpers here, e.g. vector insert/search, etc.
