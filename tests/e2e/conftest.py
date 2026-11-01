import os
import threading

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from werkzeug.serving import make_server

from app import create_app
from app.config import Config


class E2EConfig(Config):
    TESTING = True
    DATABASE = ":memory:"
    SECRET_KEY = "e2e-secret"


@pytest.fixture
def live_server_url():
    """Run the real app on a free local port in a background thread."""
    app = create_app(E2EConfig)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture
def driver():
    """A headless Chrome. Skipped on a laptop without Chrome, mandatory in CI."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    try:
        browser = webdriver.Chrome(options=options)
    except WebDriverException as error:
        if os.environ.get("CI"):
            raise
        pytest.skip(f"Chrome or its driver is not available: {str(error)[:100]}")
    browser.implicitly_wait(3)
    yield browser
    browser.quit()

