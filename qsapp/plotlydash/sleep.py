
import dash_html_components as html

import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module sleep.py loaded")

sleep_layout = html.H1(children="Sleep", className="h2 pt-3 pb-3")