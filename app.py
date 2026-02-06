from flask import Flask, render_template, request
import logging
from prometheus_client import Counter, Histogram, start_http_server

app = Flask(__name__)

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("flask-app")

# ---- Prometheus metrics ----
REQUEST_COUNT = Counter(
    "flask_requests_total",
    "Total HTTP requests"
)

REQUEST_LATENCY = Histogram(
    "flask_request_latency_seconds",
    "Request latency"
)

@app.route("/", methods=["GET", "POST"])
@REQUEST_LATENCY.time()
def login():
    REQUEST_COUNT.inc()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        logger.info(f"Login attempt for user: {username}")

        if username == "admin" and password == "secret":
            logger.info("Login successful")
            return "<h1>Login successful!</h1>"
        else:
            logger.warning("Login failed")
            return "<h1>Invalid credentials</h1>"

    logger.info("Login page accessed")
    return render_template("login.html")


if __name__ == "__main__":
    logger.info("Starting Flask application")

    # Expose /metrics on port 8001
    start_http_server(8001)

    app.run(host="0.0.0.0", port=5000)

