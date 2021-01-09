
import dash_html_components as html

import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module Heart.py loaded")

heart_layout = html.H1(children="Heart", className="h2 pt-3 pb-3")