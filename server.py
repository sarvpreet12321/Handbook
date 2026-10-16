"""
Production entry point for Render.

One web service serves the whole handbook:
  - /apps/...  -> the Dash calculators (apps/app.py)
  - everything else -> the MkDocs site, pre-built into the "site" folder

Start command on Render:  gunicorn server:server
"""
import hmac
import os

from flask import Response, redirect, request, send_from_directory

from apps.app import app

server = app.server  # the Flask server that Dash runs on

SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

# Optional password protection. Set SITE_USER and SITE_PASSWORD as
# environment variables on Render to switch it on. If they are not set,
# the site is open to anyone who has the link.
SITE_USER = os.environ.get("SITE_USER", "")
SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "")


@server.before_request
def require_login():
    if not SITE_USER or not SITE_PASSWORD:
        return None

    auth = request.authorization
    if (
        auth
        and hmac.compare_digest(auth.username or "", SITE_USER)
        and hmac.compare_digest(auth.password or "", SITE_PASSWORD)
    ):
        return None

    return Response(
        "Login required",
        401,
        {"WWW-Authenticate": 'Basic realm="AWP Mechanical Handbook"'},
    )


@server.route("/", defaults={"path": ""})
@server.route("/<path:path>")
def serve_docs(path):
    """Serve the pre-built MkDocs site. Dash keeps everything under /apps/."""
    if path == "" or path.endswith("/"):
        path = path + "index.html"
    elif os.path.isdir(os.path.join(SITE_DIR, path)):
        # MkDocs pages live at folder/index.html and need the trailing slash
        return redirect("/" + path + "/")

    if os.path.isfile(os.path.join(SITE_DIR, path)):
        return send_from_directory(SITE_DIR, path)

    if os.path.isfile(os.path.join(SITE_DIR, "404.html")):
        return send_from_directory(SITE_DIR, "404.html"), 404
    return "Page not found", 404


if __name__ == "__main__":
    # Local test only:  python server.py   then open http://127.0.0.1:8080/
    server.run(port=8080)