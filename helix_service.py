# helix_service.py
import os
from typing import Any, Dict, List

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


# ---------------------------------------------------------------------------
# Example "AddUser" query (you can keep this around as a demo or delete it)
# ---------------------------------------------------------------------------

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
    """
    Legacy demo helper. Not used by the new team-building flow.
    """
    db = init_helix_client()
    return db.query(AddUser(name, age))


# ---------------------------------------------------------------------------
# Generic helpers for your team-building flow
# ---------------------------------------------------------------------------

def run_helix_query(query_name: str, args: Dict[str, Any]) -> Any:
    """
    Run a Helix query by name, using the simple string + dict API:

        db.query("createPerson", {"name": "...", "tags": [...], "text": "..."})

    This assumes the query name exists in your Helix .hx files.
    """
    db = init_helix_client()
    # helix-py supports db.query("queryName", {"arg": value, ...})
    return db.query(query_name, args)


def apply_team_plan_to_helix(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Given the JSON plan produced by the agent, apply it to HelixDB.

    Expected plan shape (from agents_service.py instructions):

    {
      "team_name": "...",
      "team_text": "...",
      "people": [...],
      "queries": [
        {
          "query_name": "createTeam",
          "args": {"name": "...", "text": "..."}
        },
        ...
      ]
    }

    This function:

    - Iterates plan["queries"] in order
    - Calls run_helix_query(query_name, args) for each
    - Collects and returns the results, tagged with query_name
    """
    queries = plan.get("queries", [])
    results: List[Dict[str, Any]] = []

    for q in queries:
        q_name = q.get("query_name")
        q_args = q.get("args", {})

        if not q_name:
            # Skip malformed items rather than blowing up everything
            results.append(
                {
                    "query_name": None,
                    "error": "Missing query_name in plan item",
                    "raw_item": q,
                }
            )
            continue

        try:
            res = run_helix_query(q_name, q_args)
            results.append(
                {
                    "query_name": q_name,
                    "args": q_args,
                    "result": res,
                }
            )
        except Exception as e:
            # Record the error but keep processing the remaining queries
            results.append(
                {
                    "query_name": q_name,
                    "args": q_args,
                    "error": str(e),
                }
            )

    return results
