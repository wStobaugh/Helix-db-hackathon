# app.py
import os
import json
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory

from helix_service import (
    helix_add_user,
    init_helix_client,
    apply_team_plan_to_helix,
)
from selenium_service import get_page_title
from agents_service import init_agent, run_agent

# --- Flask setup ---

app = Flask(__name__, static_folder="static", static_url_path="/static")

# Initialize backends at startup
helix_client = init_helix_client()
agent = init_agent()


# --- Frontend routes ---


@app.route("/")
def index() -> Any:
    # Serve the main HTML page
    return send_from_directory(app.static_folder, "index.html")


# --- Health check ---


@app.route("/api/health", methods=["GET"])
def health() -> Any:
    return jsonify(
        {
            "status": "ok",
            "helix": bool(helix_client is not None),
        }
    )


# --- HelixDB demo endpoint (legacy example) ---


@app.route("/api/helix/users", methods=["POST"])
def api_helix_add_user() -> Any:
    """
    Example Helix endpoint: add a user with name and age
    (backed by the AddUser Query in helix_service.py).
    """
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}

    name = data.get("name")
    age = data.get("age")

    if not name or age is None:
        return jsonify({"error": "name and age are required"}), 400

    try:
        age_int = int(age)
    except ValueError:
        return jsonify({"error": "age must be an integer"}), 400

    try:
        result = helix_add_user(name, age_int)
    except Exception as e:
        return jsonify({"error": f"Helix query failed: {e}"}), 500

    return jsonify({"result": result})


# --- Selenium endpoints ---


@app.route("/api/selenium/title", methods=["POST"])
def api_selenium_title() -> Any:
    """
    Example Selenium endpoint: return the page title for a given URL.
    """
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    url = data.get("url")

    if not url:
        return jsonify({"error": "url is required"}), 400

    try:
        info = get_page_title(url)
    except Exception as e:
        return jsonify({"error": f"Selenium error: {e}"}), 500

    return jsonify(info)


# --- Generic OpenAI Agent endpoint (raw message passthrough) ---


@app.route("/api/agent", methods=["POST"])
def api_agent() -> Any:
    """
    Send a raw message string to the OpenAI Agent and return its response.
    This is a generic endpoint, mostly useful for debugging the agent.
    """
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    message = data.get("message")

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        answer = run_agent(agent, message)
    except Exception as e:
        return jsonify({"error": f"Agent error: {e}"}), 500

    return jsonify({"answer": answer})


# --- Team-building endpoint: Agent + HelixDB integration ---


@app.route("/api/team/build", methods=["POST"])
def api_team_build() -> Any:
    """
    High-level endpoint:

    INPUT JSON:
    {
      "team_name": "<desired team name>",
      "manager_prompt": "<natural language description of the team you want>",
      "linkedin_profiles": "<RAW pasted LinkedIn profile text for many people>"
    }

    FLOW:
    - Build a structured message for the agent using these fields.
    - Agent returns a JSON plan with "team_name", "team_text", "people", "queries".
    - We apply plan["queries"] to HelixDB using apply_team_plan_to_helix.
    - We return both the plan and the per-query Helix results.

    This is the main endpoint your frontend should hit.
    """
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}

    team_name = data.get("team_name")
    manager_prompt = data.get("manager_prompt")
    # raw LinkedIn profile text blob
    linkedin_raw = (
        data.get("linkedin_profiles")
        or data.get("linkedin_text")
        or data.get("profiles_raw")
    )

    if not team_name or not manager_prompt or not linkedin_raw:
        return jsonify(
            {
                "error": "team_name, manager_prompt, and linkedin_profiles (raw text) are required"
            }
        ), 400

    # Build the message expected by the agent instructions.
    # The agent knows to look for TEAM_NAME / MANAGER_PROMPT / CANDIDATES_RAW_LINKEDIN.
    message = f"""
TEAM_NAME:
{team_name}

MANAGER_PROMPT:
{manager_prompt}

CANDIDATES_RAW_LINKEDIN:
{linkedin_raw}
""".strip()

    # 1) Call the agent to get the plan JSON (as a string)
    try:
        agent_output = run_agent(agent, message)
    except Exception as e:
        return jsonify({"error": f"Agent error: {e}"}), 500

    # 2) Parse the plan JSON
    try:
        plan = json.loads(agent_output)
    except Exception as e:
        return jsonify(
            {
                "error": "Agent did not return valid JSON according to the expected schema.",
                "details": str(e),
                "raw_output": agent_output,
            }
        ), 500

    # 3) Apply the plan to HelixDB
    try:
        helix_results = apply_team_plan_to_helix(plan)
    except Exception as e:
        return jsonify(
            {
                "error": f"Failed to apply plan to HelixDB: {e}",
                "plan": plan,
            }
        ), 500

    # 4) Return both the logical plan and execution results
    return jsonify(
        {
            "plan": plan,
            "helix_results": helix_results,
        }
    )


# --- Entry point ---


if __name__ == "__main__":
    # Load environment variables if you want (optional)
    # from dotenv import load_dotenv
    # load_dotenv()

    # Expect OPENAI_API_KEY in environment for the Agents SDK.
    if not os.getenv("OPENAI_API_KEY"):
        print("[WARN] OPENAI_API_KEY is not set. Agent endpoint will fail until you set it.")

    app.run(host="0.0.0.0", port=5000, debug=True)
