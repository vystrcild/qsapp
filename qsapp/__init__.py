from flask import Flask
import logging.config

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")


def init_app():
    app = Flask(__name__)
    logger.debug("App is initialized!")
    app.config.from_object("config.DevConfig")

    with app.app_context():
        # Have to be loaded after init_app (Flask peculiarities)
        from qsapp import routes

        from .plotlydash.dashboard import init_dashboard
        app = init_dashboard(app)

    return app
