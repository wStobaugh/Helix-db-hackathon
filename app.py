# app.py
import os
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory

from helix_service import helix_add_user, init_helix_client
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


# --- HelixDB endpoints ---


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


# --- OpenAI Agent endpoint ---


@app.route("/api/agent", methods=["POST"])
def api_agent() -> Any:
    """
    Send a message to the OpenAI Agent and return its response.
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


# --- Entry point ---


if __name__ == "__main__":
    # Load environment variables if you want (optional)
    # from dotenv import load_dotenv
    # load_dotenv()

    # Expect OPENAI_API_KEY in environment for the Agents SDK.
    if not os.getenv("OPENAI_API_KEY"):
        print("[WARN] OPENAI_API_KEY is not set. Agent endpoint will fail until you set it.")

    app.run(host="0.0.0.0", port=5000, debug=True)
