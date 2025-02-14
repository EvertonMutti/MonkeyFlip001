from flask import Flask
from routes import router

from log import setup_logging
from settings import get_settings

app = Flask(__name__)
app.register_blueprint(router)
settings = get_settings()
setup_logging()

if __name__ == "__main__":
    app.run(host=settings.flaskapi_settings.host,
            port=settings.flaskapi_settings.port,
            debug=settings.flaskapi_settings.debug)
